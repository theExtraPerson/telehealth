import { TestBed } from '@angular/core/testing';

import { DoctorPortalService } from './doctor-portal.service';

describe('DoctorPortalService', () => {
  let service: DoctorPortalService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DoctorPortalService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
