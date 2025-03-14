import { CanActivateFn } from '@angular/router';

export const prescriptionGuard: CanActivateFn = (route, state) => {
  return true;
};
