from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from enum import Enum


# Enums for various status and role types
class UserRole(str, Enum):
    ADMIN = "admin"
    GURU = "guru"  # Teacher
    SISWA = "siswa"  # Student


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SanctionStatus(str, Enum):
    PENDING = "pending"
    IN_PROCESS = "in_process"
    SANCTIONED = "sanctioned"
    NOT_SANCTIONED = "not_sanctioned"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    SICK = "sick"
    EXCUSED = "excused"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


# Core User Management Models
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.SISWA)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    guru_profile: Optional["Guru"] = Relationship(back_populates="user")
    siswa_profile: Optional["Siswa"] = Relationship(back_populates="user")


# Academic Structure Models
class Jurusan(SQLModel, table=True):
    __tablename__ = "jurusan"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    code: str = Field(unique=True, max_length=10)
    description: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    kelas: List["Kelas"] = Relationship(back_populates="jurusan")


class Kelas(SQLModel, table=True):
    __tablename__ = "kelas"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)  # e.g., "XII-IPA-1"
    grade_level: int = Field()  # 10, 11, 12
    jurusan_id: int = Field(foreign_key="jurusan.id")
    wali_kelas_id: Optional[int] = Field(default=None, foreign_key="guru.id")
    capacity: int = Field(default=30)
    academic_year: str = Field(max_length=9)  # e.g., "2023/2024"
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    jurusan: Jurusan = Relationship(back_populates="kelas")
    wali_kelas: Optional["Guru"] = Relationship(back_populates="kelas_as_wali")
    siswa: List["Siswa"] = Relationship(back_populates="kelas")
    jadwal_mengajar: List["JadwalMengajar"] = Relationship(back_populates="kelas")


class Guru(SQLModel, table=True):
    __tablename__ = "guru"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    nip: str = Field(unique=True, max_length=20)  # Employee ID
    name: str = Field(max_length=100)
    gender: Gender
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    birth_date: date
    birth_place: str = Field(max_length=100)
    education: str = Field(max_length=100)  # Last education
    position: str = Field(max_length=100)  # Position/role in school
    hire_date: date
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="guru_profile")
    kelas_as_wali: List[Kelas] = Relationship(back_populates="wali_kelas")
    jadwal_mengajar: List["JadwalMengajar"] = Relationship(back_populates="guru")
    leave_requests: List["IzinGuru"] = Relationship(back_populates="guru")
    attendance_records: List["AttendanceGuru"] = Relationship(back_populates="guru")
    sanctions_initiated: List["ManajemenSanksi"] = Relationship(back_populates="initiated_by")


class Siswa(SQLModel, table=True):
    __tablename__ = "siswa"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    nis: str = Field(unique=True, max_length=20)  # Student ID
    nisn: str = Field(unique=True, max_length=20)  # National Student ID
    name: str = Field(max_length=100)
    gender: Gender
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    birth_date: date
    birth_place: str = Field(max_length=100)
    kelas_id: Optional[int] = Field(default=None, foreign_key="kelas.id")
    parent_name: str = Field(max_length=100)
    parent_phone: str = Field(max_length=20)
    enrollment_date: date
    current_points: Decimal = Field(default=Decimal("0"), decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="siswa_profile")
    kelas: Optional[Kelas] = Relationship(back_populates="siswa")
    prestasi: List["InputPrestasi"] = Relationship(back_populates="siswa")
    pelanggaran: List["InputPelanggaran"] = Relationship(back_populates="siswa")
    sanctions: List["ManajemenSanksi"] = Relationship(back_populates="siswa")
    attendance_records: List["AttendanceSiswa"] = Relationship(back_populates="siswa")


class KepalaSekolah(SQLModel, table=True):
    __tablename__ = "kepala_sekolah"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nip: str = Field(unique=True, max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    birth_date: date
    birth_place: str = Field(max_length=100)
    education: str = Field(max_length=100)
    start_date: date
    end_date: Optional[date] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Achievement and Violation System
class JenisPrestasi(SQLModel, table=True):
    __tablename__ = "jenis_prestasi"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    points: Decimal = Field(decimal_places=2)  # Points awarded for this achievement
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    prestasi_records: List["InputPrestasi"] = Relationship(back_populates="jenis_prestasi")


class JenisPelanggaran(SQLModel, table=True):
    __tablename__ = "jenis_pelanggaran"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    points_deducted: Decimal = Field(decimal_places=2)  # Points deducted for this violation
    severity_level: int = Field(default=1)  # 1-5 scale
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pelanggaran_records: List["InputPelanggaran"] = Relationship(back_populates="jenis_pelanggaran")


class InputPrestasi(SQLModel, table=True):
    __tablename__ = "input_prestasi"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    siswa_id: int = Field(foreign_key="siswa.id")
    jenis_prestasi_id: int = Field(foreign_key="jenis_prestasi.id")
    achievement_date: date
    description: str = Field(max_length=500)
    evidence: Optional[str] = Field(default=None, max_length=255)  # File path or URL
    verified: bool = Field(default=False)
    points_awarded: Decimal = Field(decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    siswa: Siswa = Relationship(back_populates="prestasi")
    jenis_prestasi: JenisPrestasi = Relationship(back_populates="prestasi_records")


class InputPelanggaran(SQLModel, table=True):
    __tablename__ = "input_pelanggaran"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    siswa_id: int = Field(foreign_key="siswa.id")
    jenis_pelanggaran_id: int = Field(foreign_key="jenis_pelanggaran.id")
    violation_date: date
    description: str = Field(max_length=500)
    evidence: Optional[str] = Field(default=None, max_length=255)  # File path or URL
    reported_by: str = Field(max_length=100)  # Name of person reporting
    points_deducted: Decimal = Field(decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    siswa: Siswa = Relationship(back_populates="pelanggaran")
    jenis_pelanggaran: JenisPelanggaran = Relationship(back_populates="pelanggaran_records")
    sanction: Optional["ManajemenSanksi"] = Relationship(back_populates="violation")


# Sanction Management
class ManajemenSanksi(SQLModel, table=True):
    __tablename__ = "manajemen_sanksi"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    siswa_id: int = Field(foreign_key="siswa.id")
    violation_id: int = Field(foreign_key="input_pelanggaran.id", unique=True)
    initiated_by_id: int = Field(foreign_key="guru.id")
    sanction_type: str = Field(max_length=100)  # Type of sanction
    sanction_description: str = Field(max_length=500)
    status: SanctionStatus = Field(default=SanctionStatus.PENDING)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    siswa: Siswa = Relationship(back_populates="sanctions")
    violation: InputPelanggaran = Relationship(back_populates="sanction")
    initiated_by: Guru = Relationship(back_populates="sanctions_initiated")


# Schedule Management
class JadwalMengajar(SQLModel, table=True):
    __tablename__ = "jadwal_mengajar"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    guru_id: int = Field(foreign_key="guru.id")
    kelas_id: int = Field(foreign_key="kelas.id")
    subject: str = Field(max_length=100)  # Subject name
    day_of_week: int = Field()  # 1-7 (Monday-Sunday)
    start_time: time
    end_time: time
    academic_year: str = Field(max_length=9)
    semester: int = Field()  # 1 or 2
    cluster: str = Field(max_length=50)  # Teaching cluster
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    guru: Guru = Relationship(back_populates="jadwal_mengajar")
    kelas: Kelas = Relationship(back_populates="jadwal_mengajar")


# Leave Management
class IzinGuru(SQLModel, table=True):
    __tablename__ = "izin_guru"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    guru_id: int = Field(foreign_key="guru.id")
    leave_type: str = Field(max_length=50)  # sick, personal, official, etc.
    start_date: date
    end_date: date
    reason: str = Field(max_length=500)
    status: LeaveStatus = Field(default=LeaveStatus.PENDING)
    approved_by: Optional[str] = Field(default=None, max_length=100)
    approval_date: Optional[datetime] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    attachment: Optional[str] = Field(default=None, max_length=255)  # File path
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    guru: Guru = Relationship(back_populates="leave_requests")


# Attendance System
class AttendanceGuru(SQLModel, table=True):
    __tablename__ = "attendance_guru"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    guru_id: int = Field(foreign_key="guru.id")
    date: date
    status: AttendanceStatus
    check_in: Optional[datetime] = Field(default=None)
    check_out: Optional[datetime] = Field(default=None)
    location_lat: Optional[Decimal] = Field(default=None, decimal_places=6)
    location_lng: Optional[Decimal] = Field(default=None, decimal_places=6)
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    guru: Guru = Relationship(back_populates="attendance_records")


class AttendanceSiswa(SQLModel, table=True):
    __tablename__ = "attendance_siswa"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    siswa_id: int = Field(foreign_key="siswa.id")
    date: date
    status: AttendanceStatus
    notes: str = Field(default="", max_length=500)
    recorded_by: str = Field(max_length=100)  # Who recorded the attendance
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    siswa: Siswa = Relationship(back_populates="attendance_records")


# Academic Calendar
class AcademicCalendar(SQLModel, table=True):
    __tablename__ = "academic_calendar"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    event_date: date
    event_type: str = Field(max_length=50)  # holiday, exam, meeting, etc.
    is_announcement: bool = Field(default=False)
    color: str = Field(default="#3498db", max_length=7)  # Hex color
    academic_year: str = Field(max_length=9)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Settings and Configuration
class SchoolSettings(SQLModel, table=True):
    __tablename__ = "school_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    school_name: str = Field(max_length=200)
    school_address: str = Field(max_length=500)
    school_phone: str = Field(max_length=20)
    school_email: str = Field(max_length=255)
    logo_path: Optional[str] = Field(default=None, max_length=255)
    favicon_path: Optional[str] = Field(default=None, max_length=255)
    geofence_enabled: bool = Field(default=False)
    geofence_lat: Optional[Decimal] = Field(default=None, decimal_places=6)
    geofence_lng: Optional[Decimal] = Field(default=None, decimal_places=6)
    geofence_radius: Optional[int] = Field(default=100)  # meters
    academic_year: str = Field(max_length=9)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and forms
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(max_length=255)
    role: UserRole


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = Field(default=None)


class GuruCreate(SQLModel, table=False):
    user_data: UserCreate
    nip: str = Field(max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    birth_date: date
    birth_place: str = Field(max_length=100)
    education: str = Field(max_length=100)
    position: str = Field(max_length=100)
    hire_date: date


class SiswaCreate(SQLModel, table=False):
    user_data: UserCreate
    nis: str = Field(max_length=20)
    nisn: str = Field(max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    birth_date: date
    birth_place: str = Field(max_length=100)
    kelas_id: Optional[int] = Field(default=None)
    parent_name: str = Field(max_length=100)
    parent_phone: str = Field(max_length=20)
    enrollment_date: date


class LeaveRequestCreate(SQLModel, table=False):
    leave_type: str = Field(max_length=50)
    start_date: date
    end_date: date
    reason: str = Field(max_length=500)


class AttendanceMarkCreate(SQLModel, table=False):
    user_id: int
    status: AttendanceStatus
    location_lat: Optional[Decimal] = Field(default=None, decimal_places=6)
    location_lng: Optional[Decimal] = Field(default=None, decimal_places=6)
    notes: str = Field(default="", max_length=500)


class PrestasiCreate(SQLModel, table=False):
    siswa_id: int
    jenis_prestasi_id: int
    achievement_date: date
    description: str = Field(max_length=500)


class PelanggaranCreate(SQLModel, table=False):
    siswa_id: int
    jenis_pelanggaran_id: int
    violation_date: date
    description: str = Field(max_length=500)
    reported_by: str = Field(max_length=100)


class SanctionCreate(SQLModel, table=False):
    violation_id: int
    sanction_type: str = Field(max_length=100)
    sanction_description: str = Field(max_length=500)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)


class CalendarEventCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    event_date: date
    event_type: str = Field(max_length=50)
    is_announcement: bool = Field(default=False)
    color: str = Field(default="#3498db", max_length=7)
