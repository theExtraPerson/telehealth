import { CanActivateFn } from '@angular/router';

export const appointmentGuard: CanActivateFn = (route, state) => {
  return true;
};
