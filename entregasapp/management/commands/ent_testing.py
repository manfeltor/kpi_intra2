from django.core.management.base import BaseCommand
from entregasapp.views import calculate_date_diff, mode_group_date_diff, mean_group_date_diff
from IPython.display import display

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        A = calculate_date_diff("fechaDespacho", "fechaEntrega", "CHEEKY", "INTERIOR")

        # print(A["date_difference"].max())
        # print(A["date_difference"].min())
        # print(A["date_difference"].std())
        # cv = A["date_difference"].std() / A["date_difference"].mean() * 100
        # print('cv: ', cv)

        b = mode_group_date_diff(A, "codigoPostal__Provincia", "date_difference", "bdDate_difference")

        print(b)

