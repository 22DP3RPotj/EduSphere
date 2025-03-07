from django.shortcuts import render


def custom_403(request, exception):
    return render(request, 'errors/403.html', {'error_message': str(exception)}, status=403)

def custom_400(request, exception):
    return render(request, 'errors/400.html', {'error_message': str(exception)}, status=400)

def custom_404(request, exception):
    return render(request, 'errors/404.html', {'error_message': str(exception)}, status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)
