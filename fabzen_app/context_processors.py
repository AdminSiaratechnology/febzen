from .models import Company,Client

def company_context(request):
    company_id = request.session.get('active_company_id')
    company_name = None
    company = None
    client = None
    company_list = []

    if request.user.is_authenticated:
        
        # Scenario 1: ADMIN
        if request.user.role == "admin":
            company_list = Company.objects.filter(user=request.user)

        # Scenario 2: CLIENT
        elif request.user.role == "client":
            try:
                client = Client.objects.get(user=request.user)
                company_list = client.company.all()
                print("client company list here",company_list)
            except Client.DoesNotExist:
                client = None

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
        'client': client,
        'company_list': company_list,

    }
