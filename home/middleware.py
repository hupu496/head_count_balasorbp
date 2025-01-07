from django.utils.timezone import now

class MidnightUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_updated = None

    def __call__(self, request):
        current_date = now().date()
        if self.last_updated != current_date:
            self.last_updated = current_date
            self.update_form_logic(request)

        response = self.get_response(request)
        return response

    def update_form_logic(self, request):
        # This logic runs only at midnight
        from home.forms import DateForm
        request.form = DateForm()  # Set the form for the new day