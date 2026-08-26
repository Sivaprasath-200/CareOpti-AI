import sys
import os
from datetime import date, timedelta
import uuid

# Add backend directory to sys path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import OperationalError
from app.db.database import SessionLocal
from app.models import (
    Hospital, Department, Ward, Bed, BedTypeEnum, BedStatusEnum,
    User, RoleEnum, DoctorDepartment,
    Patient, GenderEnum, Admission, AdmissionStatusEnum
)

def seed_data():
    db = SessionLocal()
    print("Starting synthetic data seeding...")

    try:
        # Check if DB is reachable
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
    except OperationalError:
        print("[WARNING] Database is not reachable. Seed data generation is PENDING PostgreSQL availability.")
        return

    try:
        # 1. Create Hospital
        hospital = Hospital(name="City General Hospital", address="123 Health Ave", contact_number="555-0100")
        db.add(hospital)
        db.commit()
        db.refresh(hospital)

        # 2. Create Department
        cardiology = Department(name="Cardiology", hospital_id=hospital.id)
        db.add(cardiology)
        db.commit()
        db.refresh(cardiology)

        # 3. Create Ward and Beds
        ward_a = Ward(name="Cardio Ward A", department_id=cardiology.id)
        db.add(ward_a)
        db.commit()
        db.refresh(ward_a)

        bed_1 = Bed(bed_number="A-01", ward_id=ward_a.id, bed_type=BedTypeEnum.GENERAL, status=BedStatusEnum.AVAILABLE)
        bed_2 = Bed(bed_number="A-02", ward_id=ward_a.id, bed_type=BedTypeEnum.ICU, status=BedStatusEnum.AVAILABLE)
        db.add_all([bed_1, bed_2])
        db.commit()

        # 4. Create Doctor
        doctor = User(
            email="dr.smith@hospital.com",
            password_hash="hashed_password_mock",
            name="Dr. John Smith",
            role=RoleEnum.DOCTOR,
            specialty="Cardiologist"
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        doc_dept = DoctorDepartment(doctor_id=doctor.id, department_id=cardiology.id)
        db.add(doc_dept)

        # 5. Create Patient
        patient = Patient(
            mrn=f"MRN-{uuid.uuid4().hex[:6].upper()}",
            first_name="Jane",
            last_name="Doe",
            dob=date(1980, 5, 15),
            gender=GenderEnum.FEMALE,
            blood_group="O+"
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # 6. Create Admission
        admission = Admission(
            patient_id=patient.id,
            doctor_id=doctor.id,
            bed_id=bed_1.id,
            status=AdmissionStatusEnum.ADMITTED,
            admission_date=date.today()
        )
        # Update Bed Status
        bed_1.status = BedStatusEnum.OCCUPIED

        db.add(admission)
        db.commit()

        print("Synthetic seed data inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
