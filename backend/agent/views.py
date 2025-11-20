"""
Views for the Luna admin panel
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def pdf_admin_dashboard(request):
    """
    Custom admin dashboard for PDF management
    """
    return render(request, 'pdf_admin/dashboard.html')

