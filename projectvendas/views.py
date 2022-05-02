import csv
import json
from django.shortcuts import redirect, render
from .models import Order
from .forms import OrderForm
from django.db import transaction
from datetime import datetime
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse



def list_orders(request):
    orders = Order.objects.all()
    paginator = Paginator(orders, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'orders.html', {'orders': page_obj})


def create_order(request):
    form = OrderForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('list_orders')

    return render(request, 'orders-form.html', {'form': form})


def update_order(request, id):
    order = Order.objects.get(id=id)
    form = OrderForm(request.POST or None, instance=order)

    if form.is_valid():
        form.save()
        return redirect('list_orders')

    return render(request, 'orders-form.html', {'form': form, 'order': order})


def delete_order(request, id):
    order = Order.objects.get(id=id)

    if request.method == 'POST':
        order.delete()
        return redirect('list_orders')

    return render(request, 'prod-delete-confirm.html', {'order': order})


def home(request):
    return render(request, 'index.html')

@transaction.atomic
def importer(request):
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE projectvendas_order RESTART IDENTITY;")
    
    with open('data-HQvSmRz8z8RCA5aFm4Jj5.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            if row.get('d') and row.get('h'):
                date_field = f"{row.get('d')} {row.get('h')}"
                date_field = datetime.strptime(date_field, '%Y-%m-%d %H:%M')
                order = Order(date=date_field, value=row.get('t'), quantity=row.get('qtd_p'), status=row.get('s'))
                order.save()
                
    return render(request, 'sucesso.html')


def graficos(request):
    with connection.cursor() as cursor:
        total_by_month_query = f"""
            SELECT 
                    ROUND(SUM(value), 2) AS total,
                    EXTRACT(year FROM  date) || '/' ||
                    EXTRACT(month FROM  date) as year_month
            FROM
                    projectvendas_order
            GROUP BY
                    year_month
            ORDER BY 
                    year_month
        """
        cursor.execute(total_by_month_query)
        
        total_by_month_columns = [col[0] for col in cursor.description]
        total_by_month_results =  [ dict(zip(total_by_month_columns, row)) for row in cursor.fetchall() ]
        for row in total_by_month_results:
            row['total'] = str(row.get('total')).replace(',','.')
        # print(total_by_month_results)
        
        total_by_status_query = f"""
            SELECT 
                ROUND(SUM(value), 2) AS total,
                status
            FROM
                projectvendas_order
            GROUP BY
                status
        """
        cursor.execute(total_by_status_query)
        
        total_by_status_columns = [col[0] for col in cursor.description]
        total_by_status_results =  [ dict(zip(total_by_status_columns, row)) for row in cursor.fetchall() ]
        for row in total_by_status_results:
            row['total'] = str(row.get('total')).replace(',','.')
        # print(total_by_status_results)
        
        
        top_10_days_query = f"""
            SELECT 
                ROUND(SUM(value), 2) AS total,
                date::date AS day
            FROM
                projectvendas_order
            GROUP BY
                day
            ORDER BY total DESC
            LIMIT 10
        """
        cursor.execute(top_10_days_query)
        
        top_10_days_columns = [col[0] for col in cursor.description]
        top_10_days_results =  [ dict(zip(top_10_days_columns, row)) for row in cursor.fetchall() ]
        for row in top_10_days_results:
            row['total'] = str(row.get('total')).replace(',','.')
        # print(top_10_days_results)


    return render(
        request, 
        'graficos.html', 
        {
            'top_by_month': total_by_month_results,
            'total_by_status': total_by_status_results,
            'top_10_days': top_10_days_results 
        }
    )

def export(request):
    list_of_dicts = Order.objects.all()
    

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio.csv'

    writer = csv.writer(response)
    if list_of_dicts:
        header = ['Id', 'Data', 'Valor', 'QTD_Produto', 'Status']
        writer.writerow(header)
        for row in list_of_dicts:    
            writer.writerow(
                [
                    row.id,
                    row.date,
                    row.value,
                    row.quantity,
                    row.status,
                ])
          
        print(list_of_dicts)
    return response