from rest_framework import serializers

from materials.models import Material, Category


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'code', 'price']


class CategorySerializer(serializers.ModelSerializer):
    # Список материалов в текущей категории
    materials = serializers.SerializerMethodField()

    # подкатегории текущей категории
    subcategories = serializers.SerializerMethodField()

    # Общая стоимость материалов в категории и её подкатегориях
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'total_price', 'materials', 'subcategories']

    def get_total_price(self, obj):
        # Получаем заранее рассчитанную сумму из контекста (кэш, построенный во view)
        return self.context.get('_price_cache', {}).get(obj.id, 0)

    def get_materials(self, obj):
        # Получаем материалы, принадлежащие текущей категории (без подкатегорий)
        materials = self.context.get('_materials_map', {}).get(obj.id, [])
        return MaterialSerializer(materials, many=True, context=self.context).data

    def get_subcategories(self, obj):
        # Получаем подкатегории текущей категории из кэша
        children = self.context.get('_tree_map', {}).get(obj.id, [])
        return CategorySerializer(children, many=True, context=self.context).data

