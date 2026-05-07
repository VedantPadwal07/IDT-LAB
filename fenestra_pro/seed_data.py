"""
Seed script to load sample material, pricing, and hardware data.
Run with: python seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fenestra_pro.settings')
django.setup()

from decimal import Decimal
from apps.materials.models import ProfileDatabase, GlassType, HardwareItem
from apps.pricing.models import PricingConfig

print("=" * 60)
print("SEEDING FENESTRA PRO DATABASE")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. PROFILES
# ─────────────────────────────────────────────
profiles_data = [
    # uPVC Profiles
    {'profile_code': 'FRM-001', 'profile_name': 'uPVC Frame Profile 60mm', 'profile_type': 'frame',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.680'),
     'cost_per_meter': Decimal('185.00'), 'cutting_waste_factor': Decimal('5.00'),
     'wall_thickness_mm': 60, 'rebate_depth_mm': 18},
    
    {'profile_code': 'SSH-001', 'profile_name': 'uPVC Sash Profile 45mm', 'profile_type': 'sash',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.520'),
     'cost_per_meter': Decimal('165.00'), 'cutting_waste_factor': Decimal('5.00'),
     'wall_thickness_mm': 45, 'rebate_depth_mm': 18},
    
    {'profile_code': 'MUL-001', 'profile_name': 'uPVC Mullion Profile', 'profile_type': 'mullion',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.750'),
     'cost_per_meter': Decimal('195.00'), 'cutting_waste_factor': Decimal('5.00'),
     'wall_thickness_mm': 60, 'rebate_depth_mm': 18},
    
    {'profile_code': 'BED-001', 'profile_name': 'uPVC Glazing Bead', 'profile_type': 'bead',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.180'),
     'cost_per_meter': Decimal('45.00'), 'cutting_waste_factor': Decimal('3.00'),
     'wall_thickness_mm': 15, 'rebate_depth_mm': 10},
    
    {'profile_code': 'TRK-001', 'profile_name': 'uPVC Sliding Track', 'profile_type': 'track',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.420'),
     'cost_per_meter': Decimal('135.00'), 'cutting_waste_factor': Decimal('4.00'),
     'wall_thickness_mm': 30, 'rebate_depth_mm': 12},
    
    {'profile_code': 'ILK-001', 'profile_name': 'uPVC Interlock Profile', 'profile_type': 'interlock',
     'material': 'upvc', 'standard_bar_length_mm': 6000, 'weight_per_meter_kg': Decimal('0.350'),
     'cost_per_meter': Decimal('110.00'), 'cutting_waste_factor': Decimal('4.00'),
     'wall_thickness_mm': 25, 'rebate_depth_mm': 12},

    # Aluminium Profiles
    {'profile_code': 'FRM-A01', 'profile_name': 'Aluminium Frame Profile 65mm', 'profile_type': 'frame',
     'material': 'aluminium_standard', 'standard_bar_length_mm': 6100, 'weight_per_meter_kg': Decimal('1.200'),
     'cost_per_meter': Decimal('320.00'), 'cutting_waste_factor': Decimal('4.00'),
     'wall_thickness_mm': 65, 'rebate_depth_mm': 20},
    
    {'profile_code': 'SSH-A01', 'profile_name': 'Aluminium Sash Profile 50mm', 'profile_type': 'sash',
     'material': 'aluminium_standard', 'standard_bar_length_mm': 6100, 'weight_per_meter_kg': Decimal('0.950'),
     'cost_per_meter': Decimal('285.00'), 'cutting_waste_factor': Decimal('4.00'),
     'wall_thickness_mm': 50, 'rebate_depth_mm': 20},
    
    {'profile_code': 'MUL-A01', 'profile_name': 'Aluminium Mullion Profile', 'profile_type': 'mullion',
     'material': 'aluminium_standard', 'standard_bar_length_mm': 6100, 'weight_per_meter_kg': Decimal('1.100'),
     'cost_per_meter': Decimal('340.00'), 'cutting_waste_factor': Decimal('4.00'),
     'wall_thickness_mm': 65, 'rebate_depth_mm': 20},
    
    {'profile_code': 'BED-A01', 'profile_name': 'Aluminium Glazing Bead', 'profile_type': 'bead',
     'material': 'aluminium_standard', 'standard_bar_length_mm': 6100, 'weight_per_meter_kg': Decimal('0.280'),
     'cost_per_meter': Decimal('75.00'), 'cutting_waste_factor': Decimal('3.00'),
     'wall_thickness_mm': 18, 'rebate_depth_mm': 12},
]

for p in profiles_data:
    obj, created = ProfileDatabase.objects.update_or_create(
        profile_code=p['profile_code'],
        defaults=p
    )
    status = "CREATED" if created else "UPDATED"
    print(f"  [{status}] Profile: {p['profile_code']} - {p['profile_name']} @ ₹{p['cost_per_meter']}/m")

print(f"\n✅ {len(profiles_data)} profiles loaded\n")

# ─────────────────────────────────────────────
# 2. GLASS TYPES
# ─────────────────────────────────────────────
glass_data = [
    {'name': 'Clear Float Glass', 'category': 'clear_float', 'thickness_mm': 5,
     'price_per_sqm': Decimal('450.00'), 'description': 'Standard clear float glass'},
    
    {'name': 'Tinted Glass (Grey)', 'category': 'tinted', 'thickness_mm': 6,
     'price_per_sqm': Decimal('650.00'), 'description': 'Grey tinted solar control glass'},
    
    {'name': 'Frosted Glass', 'category': 'frosted', 'thickness_mm': 5,
     'price_per_sqm': Decimal('750.00'), 'description': 'Acid-etched frosted privacy glass'},
    
    {'name': 'Tempered Safety Glass', 'category': 'tempered', 'thickness_mm': 6,
     'price_per_sqm': Decimal('1200.00'), 'description': 'Heat-treated tempered safety glass'},
    
    {'name': 'Double Glazed Unit (DGU)', 'category': 'double_glazed', 'thickness_mm': 24,
     'price_per_sqm': Decimal('2200.00'), 'description': '6mm + 12mm air gap + 6mm insulated unit'},
    
    {'name': 'Laminated Glass', 'category': 'laminated', 'thickness_mm': 10,
     'price_per_sqm': Decimal('1800.00'), 'description': 'PVB interlayer laminated safety glass'},
    
    {'name': 'Reflective Glass', 'category': 'reflective', 'thickness_mm': 6,
     'price_per_sqm': Decimal('950.00'), 'description': 'Solar reflective coated glass'},
]

for g in glass_data:
    obj, created = GlassType.objects.update_or_create(
        category=g['category'],
        defaults=g
    )
    status = "CREATED" if created else "UPDATED"
    print(f"  [{status}] Glass: {g['name']} @ ₹{g['price_per_sqm']}/sqm")

print(f"\n✅ {len(glass_data)} glass types loaded\n")

# ─────────────────────────────────────────────
# 3. HARDWARE ITEMS
# ─────────────────────────────────────────────
hardware_data = [
    # Handles
    {'code': 'HW-HDL-01', 'name': 'Espagnolette Handle (White)', 'category': 'handle',
     'unit': 'piece', 'cost_per_unit': Decimal('350.00'),
     'applies_to_types': ['casement_window', 'casement_door', 'tilt_turn', 'french_door'],
     'quantity_formula': '1_per_sash', 'description': 'Multi-point espagnolette locking handle'},
    
    {'code': 'HW-HDL-02', 'name': 'D-Handle for Sliding', 'category': 'handle',
     'unit': 'piece', 'cost_per_unit': Decimal('280.00'),
     'applies_to_types': ['sliding_window', 'sliding_door'],
     'quantity_formula': '1_per_sash', 'description': 'Flush D-handle for sliding panels'},
    
    # Locks
    {'code': 'HW-LCK-01', 'name': 'Multi-Point Lock Mechanism', 'category': 'lock',
     'unit': 'set', 'cost_per_unit': Decimal('850.00'),
     'applies_to_types': ['casement_window', 'casement_door', 'tilt_turn', 'french_door'],
     'quantity_formula': '1_per_sash', 'description': 'Multi-point locking mechanism'},
    
    {'code': 'HW-LCK-02', 'name': 'Crescent Lock (Sliding)', 'category': 'lock',
     'unit': 'piece', 'cost_per_unit': Decimal('220.00'),
     'applies_to_types': ['sliding_window', 'sliding_door'],
     'quantity_formula': '1_per_unit', 'description': 'Crescent lock for sliding sash'},
    
    # Hinges
    {'code': 'HW-HNG-01', 'name': 'Friction Stay Hinge 12"', 'category': 'hinge',
     'unit': 'piece', 'cost_per_unit': Decimal('420.00'),
     'applies_to_types': ['casement_window', 'casement_door', 'french_door'],
     'quantity_formula': '2_per_sash', 'description': '12-inch stainless steel friction stay'},
    
    {'code': 'HW-HNG-02', 'name': 'Tilt & Turn Hinge Set', 'category': 'hinge',
     'unit': 'set', 'cost_per_unit': Decimal('1200.00'),
     'applies_to_types': ['tilt_turn'],
     'quantity_formula': '1_per_sash', 'description': 'Complete tilt & turn hinge mechanism'},
    
    # Rollers
    {'code': 'HW-RLR-01', 'name': 'Tandem Roller Assembly', 'category': 'roller',
     'unit': 'set', 'cost_per_unit': Decimal('380.00'),
     'applies_to_types': ['sliding_window', 'sliding_door'],
     'quantity_formula': '1_per_sash', 'description': 'Heavy-duty tandem roller for smooth sliding'},
    
    # Seals
    {'code': 'HW-SEL-01', 'name': 'EPDM Weatherseal', 'category': 'seal',
     'unit': 'meter', 'cost_per_unit': Decimal('25.00'),
     'applies_to_types': ['casement_window', 'casement_door', 'sliding_window', 'sliding_door',
                          'fixed_window', 'french_door', 'tilt_turn', 'bi_fold_door'],
     'quantity_formula': 'perimeter_m', 'description': 'EPDM rubber weather sealing gasket'},
    
    # Mosquito Mesh
    {'code': 'HW-MSH-01', 'name': 'Fiberglass Mosquito Mesh Kit', 'category': 'mosquito_mesh',
     'unit': 'set', 'cost_per_unit': Decimal('650.00'),
     'applies_to_types': ['casement_window', 'sliding_window', 'casement_door', 'sliding_door'],
     'quantity_formula': '1_per_unit', 'description': 'Retractable fiberglass mesh with aluminium frame'},
    
    # Screw Packs
    {'code': 'HW-SCR-01', 'name': 'SS Screw Pack (Assorted)', 'category': 'screw_pack',
     'unit': 'pack', 'cost_per_unit': Decimal('120.00'),
     'applies_to_types': ['casement_window', 'casement_door', 'sliding_window', 'sliding_door',
                          'fixed_window', 'french_door', 'tilt_turn', 'bi_fold_door'],
     'quantity_formula': '1_per_unit', 'description': 'Stainless steel screw assortment pack'},
    
    # Bi-fold specific
    {'code': 'HW-BFH-01', 'name': 'Bi-fold Hinge & Track Kit', 'category': 'hinge',
     'unit': 'set', 'cost_per_unit': Decimal('2500.00'),
     'applies_to_types': ['bi_fold_door'],
     'quantity_formula': '1_per_unit', 'description': 'Complete bi-fold folding mechanism with top track'},
]

for h in hardware_data:
    obj, created = HardwareItem.objects.update_or_create(
        code=h['code'],
        defaults=h
    )
    status = "CREATED" if created else "UPDATED"
    print(f"  [{status}] Hardware: {h['code']} - {h['name']} @ ₹{h['cost_per_unit']}")

print(f"\n✅ {len(hardware_data)} hardware items loaded\n")

# ─────────────────────────────────────────────
# 4. PRICING CONFIG
# ─────────────────────────────────────────────
config, created = PricingConfig.objects.update_or_create(
    is_active=True,
    defaults={
        'name': 'Standard Pricing 2026',
        'profile_markup_percent': Decimal('25.00'),
        'glass_markup_percent': Decimal('20.00'),
        'hardware_markup_percent': Decimal('30.00'),
        'labour_cost_per_unit': Decimal('750.00'),
        'overhead_percent': Decimal('12.00'),
        'tax_rate_percent': Decimal('18.00'),
        'currency_symbol': '₹',
        'currency_code': 'INR',
        'saw_kerf_mm': 3,
        'clearance_gap_mm': 4,
    }
)
status = "CREATED" if created else "UPDATED"
print(f"  [{status}] Pricing Config: Standard Pricing 2026")
print(f"     Profile Markup: 25% | Glass Markup: 20% | Hardware Markup: 30%")
print(f"     Labour: ₹750/unit | Overhead: 12% | GST: 18%")

print("\n" + "=" * 60)
print("✅ ALL SEED DATA LOADED SUCCESSFULLY!")
print("=" * 60)
