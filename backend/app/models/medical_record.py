from datetime import datetime

class MedicalRecord:
    def __init__(self, patient_id, patient_name, date_of_birth):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.date_of_birth = date_of_birth
        self.records = []

    def add_record(self, date, description, doctor):
        self.records.append({
            'date': date,
            'description': description,
            'doctor': doctor
        })

    def get_records(self):
        return self.records

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'date_of_birth': self.date_of_birth,
            'records': self.records
        }

    def to_string(self):
        record_str = f"Medical Record for {self.patient_name} (ID: {self.patient_id})\n"
        record_str += f"Date of Birth: {self.date_of_birth}\n\n"
        for record in self.records:
            record_str += f"Date: {record['date']}\n"
            record_str += f"Description: {record['description']}\n"
            record_str += f"Doctor: {record['doctor']}\n"
            record_str += "-" * 20 + "\n"
        return record_str

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(self.to_string())

# Example usage
if __name__ == "__main__":
    mr = MedicalRecord(1, "John Doe", "1990-01-01")
    mr.add_record(datetime.now().strftime("%Y-%m-%d"), "Routine Checkup", "Dr. Smith")
    mr.add_record(datetime.now().strftime("%Y-%m-%d"), "Blood Test", "Dr. Brown")
    print(mr.to_string())
    mr.save_to_file("medical_record.txt")