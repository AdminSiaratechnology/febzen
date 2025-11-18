from .models import Company

def company_context(request):
    company_id = request.session.get('active_company_id')
    company_name = None
    company = None
    

    if company_id:
        try:
            company = Company.objects.get(company_code=company_id)
            company_name = company.company_name_street
        except Company.DoesNotExist:
            company_name = None

    return {
        'company_id': company_id,
        'company_name': company_name,
        'company': company,
    }
