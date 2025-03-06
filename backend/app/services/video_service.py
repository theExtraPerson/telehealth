from datetime import datetime
from typing import List, Optional

class VideoConsultation:
    def __init__(self, patient_id: int, doctor_id: int, start_time: datetime, end_time: datetime):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = False

    def start_consultation(self):
        self.is_active = True
        print(f"Consultation started between patient {self.patient_id} and doctor {self.doctor_id}.")

    def end_consultation(self):
        self.is_active = False
        print(f"Consultation ended between patient {self.patient_id} and doctor {self.doctor_id}.")

class VideoConsultationService:
    def __init__(self):
        self.consultations: List[VideoConsultation] = []

    def schedule_consultation(self, patient_id: int, doctor_id: int, start_time: datetime, end_time: datetime) -> VideoConsultation:
        consultation = VideoConsultation(patient_id, doctor_id, start_time, end_time)
        self.consultations.append(consultation)
        print(f"Consultation scheduled between patient {patient_id} and doctor {doctor_id} from {start_time} to {end_time}.")
        return consultation

    def get_active_consultations(self) -> List[VideoConsultation]:
        return [consultation for consultation in self.consultations if consultation.is_active]

    def find_consultation(self, patient_id: int, doctor_id: int) -> Optional[VideoConsultation]:
        for consultation in self.consultations:
            if consultation.patient_id == patient_id and consultation.doctor_id == doctor_id:
                return consultation
        return None

# Example usage
if __name__ == "__main__":
    service = VideoConsultationService()
    consultation = service.schedule_consultation(1, 101, datetime.now(), datetime.now())
    consultation.start_consultation()
    active_consultations = service.get_active_consultations()
    consultation.end_consultation()