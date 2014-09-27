from django.contrib.admin.filters import SimpleListFilter

class NullFilterSpec(SimpleListFilter):
    title = u''

    parameter_name = u''

    def lookups(self, request, model_admin):
        return (
            ('1', 'Есть'),
            ('0', 'Нет'),
        )

    def queryset(self, request, queryset):
		kwargs = {'%s__isnull'%self.parameter_name : True}
		if self.value() == '1':
			return queryset.exclude(**kwargs)
		if self.value() == '0':
			return queryset.filter(**kwargs)
		return queryset