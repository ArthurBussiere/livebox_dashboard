import { Component, inject, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ToastComponent } from './shared/toast/toast';
import { AppHeader } from './shared/app-header/app-header';
import { SafeHtmlPipe } from './shared/safe-html.pipe';
import { DeviceRegistryService } from './core/device-registry.service';
import { LayoutService } from './core/layout.service';
import { AuthService } from './core/auth.service';

const SVG = (path: string) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">${path}</svg>`;

const ICONS = {
  devices: SVG(
    '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
  ),
  wifi: SVG(
    '<path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1" fill="currentColor" stroke="none"/>',
  ),
  firewall: SVG(
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  ),
  dhcp: SVG(
    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
  ),
  dyndns: SVG(
    '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
  ),
  system: SVG(
    '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  ),
  lan: SVG(
    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>',
  ),
};

interface NavItem { path: string; label: string; icon: string; }

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ToastComponent, AppHeader, SafeHtmlPipe],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private readonly registry = inject(DeviceRegistryService);
  readonly layout = inject(LayoutService);
  readonly auth = inject(AuthService);

  protected readonly nav: NavItem[] = [
    { path: '/devices',  label: 'Devices',   icon: ICONS.devices  },
    { path: '/wifi',     label: 'WiFi',       icon: ICONS.wifi     },
    { path: '/firewall', label: 'Firewall',   icon: ICONS.firewall },
    { path: '/dhcp',     label: 'DHCP',       icon: ICONS.dhcp     },
    { path: '/dyndns',   label: 'DynDNS',     icon: ICONS.dyndns   },
    { path: '/system',   label: 'System',     icon: ICONS.system   },
    { path: '/lan',      label: 'LAN Stats',  icon: ICONS.lan      },
  ];

  ngOnInit(): void {
    this.registry.load();
  }
}
