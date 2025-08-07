class EsewaPayment:
    def __init__(self, product_code, success_url, failure_url, secret_key):
        self.product_code = product_code
        self.success_url = success_url
        self.failure_url = failure_url
        self.secret_key = secret_key

    def create_signature(self, total_amount, transaction_uuid):
        pass  # Add logic here

    def generate_form(self):
        return "<form>Esewa Payment Form</form>"
