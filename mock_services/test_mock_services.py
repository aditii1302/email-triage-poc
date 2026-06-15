from mock_services.itsm_a import create_ticket
from mock_services.itsm_b import create_incident
from mock_services.directory_service import get_user

print(
    create_ticket({})
)

print(
    create_incident({})
)

print(
    get_user("john@example.com")
)