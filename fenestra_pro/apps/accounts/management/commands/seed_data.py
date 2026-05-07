"""Seed the database with sample data for testing."""
from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.accounts.models import CustomUser
from apps.materials.models import ProfileDatabase, GlassType, HardwareItem
from apps.pricing.models import PricingConfig


class Command(BaseCommand):
    help = 'Seed database with sample profiles, glass types, hardware, and users.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create users
        if not CustomUser.objects.filter(username='maker').exists():
            CustomUser.objects.create_superuser(
                username='maker', email='maker@fenestra.com', password='maker123',
                role='maker', first_name='Admin', last_name='Maker',
                company_name='Fenestra Manufacturing Co.'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Maker user created (maker/maker123)'))

        if not CustomUser.objects.filter(username='customer1').exists():
            CustomUser.objects.create_user(
                username='customer1', email='customer@test.com', password='customer123',
                role='customer', first_name='Rahul', last_name='Sharma',
                company_name='Dream Homes Builders', phone='+91 98765 43210',
                city='Mumbai'
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Customer user created (customer1/customer123)'))

        # Pricing Config
        PricingConfig.objects.get_or_create(is_active=True, defaults={
            'name': 'Standard Pricing 2026',
            'profile_markup_percent': Decimal('25'),
            'glass_markup_percent': Decimal('20'),
            'hardware_markup_percent': Decimal('30'),
            'labour_cost_per_unit': Decimal('500'),
            'overhead_percent': Decimal('10'),
            'tax_rate_percent': Decimal('18'),
            'currency_symbol': '₹',
            'saw_kerf_mm': 3,
            'clearance_gap_mm': 4,
        })
        self.stdout.write(self.style.SUCCESS('  ✓ Pricing config created'))

        # Profiles
        profiles = [
            ('FRM-UPVC-60', 'uPVC Frame 60mm', 'frame', 'upvc', 60, 18, Decimal('0.85'), Decimal('120')),
            ('SSH-UPVC-45', 'uPVC Sash 45mm', 'sash', 'upvc', 45, 15, Decimal('0.65'), Decimal('95')),
            ('MUL-UPVC-60', 'uPVC Mullion 60mm', 'mullion', 'upvc', 60, 18, Decimal('0.70'), Decimal('100')),
            ('BED-UPVC-18', 'uPVC Glazing Bead', 'bead', 'upvc', 18, 10, Decimal('0.15'), Decimal('35')),
            ('TRK-UPVC-30', 'uPVC Sliding Track', 'track', 'upvc', 30, 0, Decimal('0.40'), Decimal('75')),
            ('ILK-UPVC-25', 'uPVC Interlock', 'interlock', 'upvc', 25, 0, Decimal('0.30'), Decimal('60')),
            ('THR-UPVC-40', 'uPVC Threshold', 'threshold', 'upvc', 40, 0, Decimal('0.55'), Decimal('85')),
            ('FRM-ALU-50', 'Aluminium Frame 50mm', 'frame', 'aluminium_standard', 50, 15, Decimal('0.95'), Decimal('180')),
            ('SSH-ALU-40', 'Aluminium Sash 40mm', 'sash', 'aluminium_standard', 40, 12, Decimal('0.75'), Decimal('150')),
            ('MUL-ALU-50', 'Aluminium Mullion', 'mullion', 'aluminium_standard', 50, 15, Decimal('0.80'), Decimal('160')),
        ]
        for code, name, ptype, mat, wall, rebate, weight, cost in profiles:
            ProfileDatabase.objects.get_or_create(profile_code=code, defaults={
                'profile_name': name, 'profile_type': ptype, 'material': mat,
                'wall_thickness_mm': wall, 'rebate_depth_mm': rebate,
                'weight_per_meter_kg': weight, 'cost_per_meter': cost,
            })
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(profiles)} profiles created'))

        # Glass Types
        glass = [
            ('Clear Float Glass', 'clear_float', 5, Decimal('450')),
            ('Tinted Glass', 'tinted', 6, Decimal('650')),
            ('Frosted Glass', 'frosted', 5, Decimal('700')),
            ('Tempered Glass', 'tempered', 8, Decimal('950')),
            ('Double Glazed Unit', 'double_glazed', 20, Decimal('1800')),
            ('Laminated Glass', 'laminated', 10, Decimal('1200')),
            ('Reflective Glass', 'reflective', 6, Decimal('850')),
        ]
        for name, cat, thick, price in glass:
            GlassType.objects.get_or_create(category=cat, defaults={
                'name': name, 'thickness_mm': thick, 'price_per_sqm': price,
            })
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(glass)} glass types created'))

        # Hardware
        all_types = ['sliding_window', 'casement_window', 'fixed_window', 'sliding_door',
                     'casement_door', 'french_door', 'bi_fold_door', 'tilt_turn']
        sliding = ['sliding_window', 'sliding_door']
        casement = ['casement_window', 'casement_door', 'french_door', 'tilt_turn']

        hardware = [
            ('HW-HDL-01', 'Crescent Lock Handle', 'handle', 'piece', Decimal('250'), sliding, '1_per_sash'),
            ('HW-HDL-02', 'Lever Handle Set', 'handle', 'set', Decimal('450'), casement, '1_per_sash'),
            ('HW-HNG-01', 'Friction Stay Hinge 12"', 'hinge', 'piece', Decimal('180'), casement, '2_per_sash'),
            ('HW-RLR-01', 'Tandem Roller Set', 'roller', 'set', Decimal('350'), sliding, '1_per_sash'),
            ('HW-LCK-01', 'Multi-Point Lock', 'lock', 'piece', Decimal('550'), casement, '1_per_sash'),
            ('HW-SEL-01', 'EPDM Gasket Seal', 'seal', 'meter', Decimal('25'), all_types, 'perimeter_m'),
            ('HW-SCR-01', 'SS Screw Pack', 'screw_pack', 'pack', Decimal('85'), all_types, '1_per_unit'),
            ('HW-WS-01', 'Weather Strip', 'weather_strip', 'meter', Decimal('30'), all_types, 'perimeter_m'),
            ('HW-MSH-01', 'Mosquito Mesh Kit', 'mosquito_mesh', 'set', Decimal('650'), all_types, '1_per_unit'),
        ]
        for code, name, cat, unit, cost, types, formula in hardware:
            HardwareItem.objects.get_or_create(code=code, defaults={
                'name': name, 'category': cat, 'unit': unit, 'cost_per_unit': cost,
                'applies_to_types': types, 'quantity_formula': formula,
            })
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(hardware)} hardware items created'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('  Login as maker: maker / maker123')
        self.stdout.write('  Login as customer: customer1 / customer123')
