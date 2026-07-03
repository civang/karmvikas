import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    EMPLOYEE = "employee"


class LeaveType(str, enum.Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    UNPAID = "unpaid"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"


class DocumentType(str, enum.Enum):
    ID_PROOF = "id_proof"
    OFFER_LETTER = "offer_letter"
    RESUME = "resume"
    CERTIFICATE = "certificate"
    OTHER = "other"


class CalendarEventType(str, enum.Enum):
    HOLIDAY = "holiday"
    MEETING = "meeting"
    DEADLINE = "deadline"
    EVENT = "event"
    OTHER = "other"
