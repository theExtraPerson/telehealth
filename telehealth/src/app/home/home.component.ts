import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  title = 'KMC-Hospital';
  vision = 'To be the preferred \'at home\' centre of care with atouch of passion in healthcare delivery aimed at building legacy in human health needs for the pleasure of Allah.';
  mission = 'To be the leading centre of excellency in providing affordable and accessible healthcare that: \n' +
    ' Patients recommend to family and friends, \n' +
    ' Physicians prefer for their patients, \n' + 
    ' Purchasers select for their clients, \n' +
    ' Employees are proud of, and \n' +
    ' Investors seek for long-term returns.';
  coreValues = [
    'Compassion',
    'Respect and Integrity',
    'Innovation and Excellence',
    'Accountability and Professionalism',
    'Teamwork and Patient Centric',
    'Empathy and Quality Care'
  ];
  services = [
    {
      name: 'Primary Care',
      description: 'Our primary care services include routine check-ups, health screenings, and management of chronic conditions.',
      link: '/book-appointment/primary-care'
    },
    {
      name: 'Specialty Care',
      description: 'Our specialty care services include cardiology, oncology, and neurology.',
      link: '/book-appointment/specialty-care'
    },
    {
      name: 'Urgent Care',
      description: 'Our urgent care services include treatment for minor injuries and illnesses.',
      link: '/book-appointment/urgent-care'
    }
  ]; 
}
