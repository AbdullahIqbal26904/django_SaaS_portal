# Create a test department and service package
from department.models import Department
from service_package.models import ServicePackage
from user.models import User
from datetime import datetime

# Create a test department
department = Department.objects.create(
    name="Test Department",
    description="A test department for testing purposes"
)

# Create a service package
service_package = ServicePackage.objects.create(
    name="Basic Package",
    description="A basic service package for testing",
    price=19.99,
    billing_cycle="monthly",
    features={
        "Feature 1": "Basic",
        "Feature 2": "Included",
        "Feature 3": "Not included"
    },
    is_active=True
)

print(f"Created department: {department.name}")
print(f"Created service package: {service_package.name}")
