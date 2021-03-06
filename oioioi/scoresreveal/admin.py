from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from oioioi.base import admin
from oioioi.contests.admin import SubmissionAdmin
from oioioi.scoresreveal.utils import is_revealed
from oioioi.scoresreveal.models import ScoreRevealConfig


class RevealedFilter(SimpleListFilter):
    title = _("revealed")
    parameter_name = 'revealed'

    def lookups(self, request, model_admin):
        return (
            (1, _("Yes")),
            (0, _("No"))
        )

    def queryset(self, request, queryset):
        if self.value():
            isnull = self.value() == '0'
            return queryset.filter(revealed__isnull=isnull)
        else:
            return queryset


class ScoresRevealConfigInline(admin.TabularInline):
    model = ScoreRevealConfig
    can_delete = True
    extra = 0


class ScoresRevealProgrammingProblemAdminMixin(object):
    def __init__(self, *args, **kwargs):
        super(ScoresRevealProgrammingProblemAdminMixin, self) \
            .__init__(*args, **kwargs)
        self.inlines = self.inlines + [ScoresRevealConfigInline]


class ScoresRevealSubmissionAdminMixin(object):
    def __init__(self, *args, **kwargs):
        super(ScoresRevealSubmissionAdminMixin, self).__init__(*args, **kwargs)
        self.list_display = self.list_display + ['reveal_display']
        self.list_filter = self.list_filter + [RevealedFilter]

    def reveal_display(self, instance):
        return is_revealed(instance)
    reveal_display.short_description = _("Revealed")
    reveal_display.admin_order_field = 'revealed'
    reveal_display.boolean = True

    def get_list_select_related(self):
        return super(ScoresRevealSubmissionAdminMixin, self). \
                get_list_select_related() + ['revealed']

SubmissionAdmin.mix_in(ScoresRevealSubmissionAdminMixin)
