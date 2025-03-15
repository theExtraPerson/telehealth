class PrescriptionService:
    def __init__(self, prescription_repository, notification_service):
        self.prescription_repository = prescription_repository
        self.notification_service = notification_service

    def serve_prescription(self, prescription_id, patient_id):
        prescription = self.prescription_repository.get_prescription(prescription_id)
        if not prescription:
            raise ValueError("Prescription not found")
        
        if prescription.patient_id != patient_id:
            raise ValueError("Prescription does not belong to the patient")
        
        if prescription.is_expired():
            raise ValueError("Prescription is expired")
        
        prescription.mark_as_served()
        self.prescription_repository.update_prescription(prescription)
        self.notification_service.notify_patient(patient_id, "Your prescription has been served.")

    def refill_prescription(self, prescription_id, patient_id):
        prescription = self.prescription_repository.get_prescription(prescription_id)
        if not prescription:
            raise ValueError("Prescription not found")
        
        if prescription.patient_id != patient_id:
            raise ValueError("Prescription does not belong to the patient")
        
        if not prescription.can_be_refilled():
            raise ValueError("Prescription cannot be refilled")
        
        prescription.refill()
        self.prescription_repository.update_prescription(prescription)
        self.notification_service.notify_patient(patient_id, "Your prescription has been refilled.")

    def request_prescription(self, patient_id, medication_id, dosage, frequency):
        new_prescription = self.prescription_repository.create_prescription(
            patient_id=patient_id,
            medication_id=medication_id,
            dosage=dosage,
            frequency=frequency
        )
        self.notification_service.notify_patient(patient_id, "Your prescription request has been submitted.")
        return new_prescription