import uuid
from app.db.database import SessionLocal
from app.models.users import User, RoleEnum
from app.models.patient import Patient
from app.models.hospital import Hospital, Department, Ward, Bed, BedTypeEnum, BedStatusEnum, DoctorDepartment
from app.models.clinical import Admission, AdmissionStatusEnum
def seed_resources():
    db = SessionLocal()
    
    # Check if hospital exists
    hospital = db.query(Hospital).first()
    if not hospital:
        hospital = Hospital(name="City Central Hospital")
        db.add(hospital)
        db.commit()
        db.refresh(hospital)

    # Check if we already seeded
    if db.query(Department).count() > 0:
        print("Resources already seeded.")
        # But we need to make sure we have a fresh state for testing (beds available)
        beds = db.query(Bed).all()
        for b in beds:
            b.status = BedStatusEnum.AVAILABLE
        db.commit()
        return

    # Seed Departments
    d_cardio = Department(name="Cardiology", hospital_id=hospital.id)
    d_er = Department(name="Emergency", hospital_id=hospital.id)
    d_gen = Department(name="General Medicine", hospital_id=hospital.id)
    db.add_all([d_cardio, d_er, d_gen])
    db.commit()

    # Seed Wards
    w_cardio_icu = Ward(name="Cardiology ICU", department_id=d_cardio.id)
    w_er_trauma = Ward(name="ER Trauma", department_id=d_er.id)
    w_gen_1 = Ward(name="General Ward 1", department_id=d_gen.id)
    db.add_all([w_cardio_icu, w_er_trauma, w_gen_1])
    db.commit()

    # Seed Beds
    beds = []
    # 2 ICU beds in ER
    for i in range(1, 3):
        beds.append(Bed(bed_number=f"ER-ICU-{i}", ward_id=w_er_trauma.id, bed_type=BedTypeEnum.ICU))
    # 3 General beds in Gen 1
    for i in range(1, 4):
        beds.append(Bed(bed_number=f"GEN-{i}", ward_id=w_gen_1.id, bed_type=BedTypeEnum.GENERAL))
        
    db.add_all(beds)
    db.commit()

    # Seed Doctors
    u1 = User(
        email="doc.er@hospital.com",
        username="dr_er",
        hashed_password="dummy_hash_for_test",
        role=RoleEnum.DOCTOR,
        first_name="Alice",
        last_name="Smith"
    )
    u2 = User(
        email="doc.gen@hospital.com",
        username="dr_gen",
        hashed_password="dummy_hash_for_test",
        role=RoleEnum.DOCTOR,
        first_name="Bob",
        last_name="Jones"
    )
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)
    
    # Map doctors to departments
    db.add(DoctorDepartment(doctor_id=u1.id, department_id=d_er.id))
    db.add(DoctorDepartment(doctor_id=u2.id, department_id=d_gen.id))
    db.commit()

    print("Seed complete.")

if __name__ == "__main__":
    seed_resources()
