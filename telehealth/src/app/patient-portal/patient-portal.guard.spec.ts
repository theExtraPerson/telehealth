import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { patientPortalGuard } from './patient-portal.guard';

describe('patientPortalGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => patientPortalGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
