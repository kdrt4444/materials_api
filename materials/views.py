from rest_framework import viewsets, status
from collections import defaultdict
from decimal import Decimal

import pandas as pd
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from materials.models import Material, Category
from materials.serializers import MaterialSerializer, CategorySerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    lookup_field = 'code'
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'], url_path='upload-excel')
    def upload_excel(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'Файл не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(excel_file)

            # Проверка наличия обязательных столбцов
            required_columns = {'name', 'category_code', 'code', 'price'}
            if not required_columns.issubset(df.columns):
                return Response({'error': f'Файл должен содержать столбцы: {required_columns}'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Загружаем все категории и материалы
            categories = Category.objects.all()
            category_map = {cat.code: cat for cat in categories}

            existing_materials = Material.objects.all()
            material_map = {m.code: m for m in existing_materials}

            to_create = []
            to_update = []
            errors = []

            # Обрабатываем строки таблицы: обновляем или добавляем материалы
            for _, row in df.iterrows():
                name = str(row['name'])
                category_code = str(row['category_code'])
                code = str(row['code'])
                price = Decimal(str(row['price']))

                category = category_map.get(category_code)
                if not category:
                    errors.append(f"Категория {category_code} не найдена")
                    continue

                if code in material_map:
                    # Обновляем существующий материал
                    material = material_map[code]
                    material.name = name
                    material.price = price
                    material.category = category
                    to_update.append(material)
                else:
                    # Создаём новый материал
                    to_create.append(Material(
                        name=name,
                        code=code,
                        price=price,
                        category=category
                    ))

            # Выполняем bulk-операции для производительности (2 запроса)
            if to_update:
                Material.objects.bulk_update(to_update, ['name', 'price', 'category'])

            if to_create:
                Material.objects.bulk_create(to_create)

            return Response({
                'created': len(to_create),
                'updated': len(to_update),
                'errors': errors
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'code'

    def list(self, request, *args, **kwargs):
        # Загружаем все категории и корневые узлы
        all_categories = self.get_queryset()
        roots = all_categories.filter(parent__isnull=True)

        # Загружаем все материалы и связываем их с категориями
        all_materials = Material.objects.select_related('category').all()

        # Строим кэши для сериализации
        context = self._build_caches(all_categories, all_materials)

        serializer = self.get_serializer(roots, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Загружаем выбранную категорию и всех её потомков
        instance = self.get_object()
        descendants = instance.get_descendants(include_self=True).select_related('parent')

        # Загружаем материалы, относящиеся к этим категориям
        materials = Material.objects.filter(category__in=descendants).select_related('category')

        # Строим кэш для сериализации
        context = self._build_caches(descendants, materials)

        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data)

    def _build_caches(self, categories, materials):
        price_cache = defaultdict(Decimal)  # id категории: total_price
        tree_map = defaultdict(list)  # дерево категорий
        materials_map = defaultdict(list)  # id категории: список materials

        # Группируем материалы по категориям
        for mat in materials:
            materials_map[mat.category_id].append(mat)

        # Строим дерево подкатегорий
        for cat in categories:
            if cat.parent_id:
                tree_map[cat.parent_id].append(cat)

        # Считаем сумму материалов внутри каждой категории
        for cat in categories:
            price_cache[cat.id] = Decimal(sum(m.price for m in materials_map[cat.id]))

        # Проходим по дереву снизу вверх: суммируем стоимости потомков к родителю
        for cat in sorted(categories, key=lambda c: -c.level):
            if cat.parent_id:
                price_cache[cat.parent_id] += price_cache[cat.id]

        # Собранные данные передаём в сериализатор
        return {
            '_price_cache': price_cache,
            '_tree_map': tree_map,
            '_materials_map': materials_map,
        }
