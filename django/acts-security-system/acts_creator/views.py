from django.shortcuts import render


def main_page(request):
    return render(request, 'acts_creator/main_page.html', {})
