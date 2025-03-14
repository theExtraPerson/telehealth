import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { appointmentGuard } from './appointment.guard';

describe('appointmentGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => appointmentGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
