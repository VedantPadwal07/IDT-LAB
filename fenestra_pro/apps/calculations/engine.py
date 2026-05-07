"""
Core Calculation Engine for FENESTRA PRO.
Handles profile cutting, glass sizing, hardware BOQ, and bar optimization.
"""
from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class CutPiece:
    """A single cut piece of profile."""
    profile_code: str
    profile_name: str
    description: str
    length_mm: int
    quantity: int
    cut_angle: str
    cost_per_meter: Decimal = Decimal('0')

    @property
    def total_length_mm(self):
        return self.length_mm * self.quantity

    @property
    def length_m(self):
        return Decimal(str(self.length_mm)) / Decimal('1000')

    @property
    def cost(self):
        return self.length_m * self.quantity * self.cost_per_meter


@dataclass
class GlassPiece:
    """A glass panel specification."""
    description: str
    width_mm: int
    height_mm: int
    glass_type: str
    thickness_mm: int
    quantity: int

    @property
    def area_sqm(self):
        return Decimal(str(self.width_mm * self.height_mm)) / Decimal('1000000')

    @property
    def total_area_sqm(self):
        return self.area_sqm * self.quantity


@dataclass
class HardwareBOQItem:
    """A hardware item in the bill of quantities."""
    code: str
    name: str
    category: str
    unit: str
    quantity: int
    cost_per_unit: Decimal = Decimal('0')

    @property
    def total_cost(self):
        return self.cost_per_unit * self.quantity


@dataclass
class BarCut:
    """Represents cuts on a single bar."""
    bar_number: int
    cuts: list = field(default_factory=list)
    bar_length_mm: int = 6000

    @property
    def used_mm(self):
        return sum(c['length'] + c.get('kerf', 3) for c in self.cuts)

    @property
    def waste_mm(self):
        return self.bar_length_mm - self.used_mm

    @property
    def waste_percent(self):
        if self.bar_length_mm == 0:
            return 0
        return round(self.waste_mm / self.bar_length_mm * 100, 1)


@dataclass
class OptimizationResult:
    """Result of bar cutting optimization."""
    profile_code: str
    profile_name: str
    bars: list = field(default_factory=list)
    total_bars: int = 0
    total_waste_mm: int = 0
    waste_percent: float = 0
    bar_length_mm: int = 6000


@dataclass
class CalculationResult:
    """Complete calculation result for a design."""
    design_code: str
    cut_pieces: list = field(default_factory=list)
    glass_pieces: list = field(default_factory=list)
    hardware_items: list = field(default_factory=list)
    bar_optimizations: list = field(default_factory=list)
    cost_breakdown: dict = field(default_factory=dict)


class CalculationEngine:
    """
    Master calculation engine for window/door fabrication.
    Computes profile cuts, glass sizes, hardware BOQ, and bar optimization.
    """

    # Default profile dimensions (mm) - overridden by actual profile data
    DEFAULT_FRAME_WALL = 60
    DEFAULT_SASH_WALL = 45
    DEFAULT_REBATE_DEPTH = 18
    DEFAULT_INTERLOCK = 25
    DEFAULT_TRACK_HEIGHT = 30

    def calculate(self, design, profiles=None, glass_types=None, hardware_items=None, pricing_config=None):
        """
        Run the full calculation pipeline for a design.

        Args:
            design: WindowDoorDesign instance
            profiles: QuerySet of ProfileDatabase (optional, will query if not provided)
            glass_types: QuerySet of GlassType (optional)
            hardware_items: QuerySet of HardwareItem (optional)
            pricing_config: PricingConfig instance (optional)

        Returns:
            CalculationResult with all calculations
        """
        from apps.materials.models import ProfileDatabase, GlassType, HardwareItem as HWModel
        from apps.pricing.models import PricingConfig as PConfig

        if profiles is None:
            profiles = ProfileDatabase.objects.filter(is_active=True, material=design.frame_material)
        if glass_types is None:
            glass_types = GlassType.objects.filter(is_active=True)
        if hardware_items is None:
            hardware_items = HWModel.objects.filter(is_active=True)
        if pricing_config is None:
            pricing_config = PConfig.get_active()

        # Get profile dimensions from DB or use defaults
        frame_profile = profiles.filter(profile_type='frame').first()
        sash_profile = profiles.filter(profile_type='sash').first()

        fw = frame_profile.wall_thickness_mm if frame_profile else self.DEFAULT_FRAME_WALL
        sw = sash_profile.wall_thickness_mm if sash_profile else self.DEFAULT_SASH_WALL
        rd = frame_profile.rebate_depth_mm if frame_profile else self.DEFAULT_REBATE_DEPTH
        gap = pricing_config.clearance_gap_mm
        kerf = pricing_config.saw_kerf_mm

        # 1. Calculate profile cuts
        cut_pieces = self._calculate_profile_cuts(
            design, profiles, fw, sw, rd
        )

        # 2. Calculate glass sizes
        glass_pieces = self._calculate_glass(
            design, glass_types, fw, rd, gap
        )

        # 3. Calculate hardware BOQ
        hw_boq = self._calculate_hardware(
            design, hardware_items
        )

        # 4. Optimize bar cutting
        bar_opts = self._optimize_bars(cut_pieces, profiles, kerf)

        # 5. Calculate costs
        cost_breakdown = self._calculate_costs(
            cut_pieces, glass_pieces, hw_boq, bar_opts,
            design, glass_types, pricing_config
        )

        result = CalculationResult(
            design_code=design.code,
            cut_pieces=[self._piece_to_dict(p) for p in cut_pieces],
            glass_pieces=[self._glass_to_dict(g) for g in glass_pieces],
            hardware_items=[self._hw_to_dict(h) for h in hw_boq],
            bar_optimizations=[self._opt_to_dict(o) for o in bar_opts],
            cost_breakdown=cost_breakdown,
        )
        return result

    def _calculate_profile_cuts(self, design, profiles, fw, sw, rd):
        """Calculate all profile cutting lengths based on design type."""
        W = design.width_mm
        H = design.height_mm
        panels = design.num_panels
        qty = design.quantity
        dt = design.design_type

        frame_profile = profiles.filter(profile_type='frame').first()
        sash_profile = profiles.filter(profile_type='sash').first()
        mullion_profile = profiles.filter(profile_type='mullion').first()
        bead_profile = profiles.filter(profile_type='bead').first()
        track_profile = profiles.filter(profile_type='track').first()
        interlock_profile = profiles.filter(profile_type='interlock').first()

        f_code = frame_profile.profile_code if frame_profile else 'FRM-001'
        f_name = frame_profile.profile_name if frame_profile else 'Frame Profile'
        f_cost = frame_profile.cost_per_meter if frame_profile else Decimal('0')
        s_code = sash_profile.profile_code if sash_profile else 'SSH-001'
        s_name = sash_profile.profile_name if sash_profile else 'Sash Profile'
        s_cost = sash_profile.cost_per_meter if sash_profile else Decimal('0')

        pieces = []

        # Frame pieces (common to all types)
        frame_top = W - (2 * fw)
        frame_bottom = W - (2 * fw)
        frame_left = H - (2 * fw)
        frame_right = H - (2 * fw)

        cut_angle = '45deg' if dt in ('casement_window', 'casement_door', 'french_door', 'tilt_turn') else '90deg'

        pieces.append(CutPiece(f_code, f_name, 'Frame Top Rail', max(frame_top, 0), qty, cut_angle, f_cost))
        pieces.append(CutPiece(f_code, f_name, 'Frame Bottom Rail', max(frame_bottom, 0), qty, cut_angle, f_cost))
        pieces.append(CutPiece(f_code, f_name, 'Frame Left Stile', max(frame_left, 0), qty, cut_angle, f_cost))
        pieces.append(CutPiece(f_code, f_name, 'Frame Right Stile', max(frame_right, 0), qty, cut_angle, f_cost))

        # Type-specific sash calculations
        if dt == 'sliding_window':
            panel_w = int((W - (2 * fw)) / panels)
            sash_h = H - (2 * fw) - self.DEFAULT_TRACK_HEIGHT
            for i in range(panels):
                label = f'Sash {i+1}'
                pieces.append(CutPiece(s_code, s_name, f'{label} Top Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Bottom Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Left Stile', sash_h, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Right Stile', sash_h, qty, '90deg', s_cost))
            if interlock_profile and panels > 1:
                pieces.append(CutPiece(interlock_profile.profile_code, interlock_profile.profile_name,
                    'Interlock', sash_h, qty * (panels - 1), '90deg',
                    interlock_profile.cost_per_meter))
            if track_profile:
                pieces.append(CutPiece(track_profile.profile_code, track_profile.profile_name,
                    'Track', W - (2 * fw), qty * 2, '90deg', track_profile.cost_per_meter))

        elif dt == 'casement_window':
            sash_w = int((W - (2 * fw) - (max(panels - 1, 0) * sw)) / panels)
            sash_h = H - (2 * fw)
            for i in range(panels):
                label = f'Sash {i+1}'
                pieces.append(CutPiece(s_code, s_name, f'{label} Top Rail', sash_w, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Bottom Rail', sash_w, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Left Stile', sash_h, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Right Stile', sash_h, qty, '45deg', s_cost))

        elif dt == 'fixed_window':
            pass  # No sash for fixed windows

        elif dt == 'sliding_door':
            panel_w = int((W - (2 * fw)) / panels)
            sash_h = H - fw - self.DEFAULT_TRACK_HEIGHT
            for i in range(panels):
                label = f'Panel {i+1}'
                pieces.append(CutPiece(s_code, s_name, f'{label} Top Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Bottom Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Left Stile', sash_h, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Right Stile', sash_h, qty, '90deg', s_cost))
            if track_profile:
                pieces.append(CutPiece(track_profile.profile_code, track_profile.profile_name,
                    'Door Track', W - (2 * fw), qty * 2, '90deg', track_profile.cost_per_meter))

        elif dt in ('casement_door', 'french_door', 'tilt_turn'):
            sash_w = int((W - (2 * fw) - (max(panels - 1, 0) * sw)) / panels)
            sash_h = H - (2 * fw)
            for i in range(panels):
                label = f'Leaf {i+1}'
                pieces.append(CutPiece(s_code, s_name, f'{label} Top Rail', sash_w, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Bottom Rail', sash_w, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Left Stile', sash_h, qty, '45deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Right Stile', sash_h, qty, '45deg', s_cost))

        elif dt == 'bi_fold_door':
            panel_w = int((W - (2 * fw)) / panels)
            sash_h = H - (2 * fw)
            for i in range(panels):
                label = f'Fold {i+1}'
                pieces.append(CutPiece(s_code, s_name, f'{label} Top Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Bottom Rail', panel_w, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Left Stile', sash_h, qty, '90deg', s_cost))
                pieces.append(CutPiece(s_code, s_name, f'{label} Right Stile', sash_h, qty, '90deg', s_cost))

        # Mullions (vertical dividers between panels)
        if mullion_profile and panels > 1 and dt not in ('sliding_window', 'sliding_door'):
            mullion_len = H - (2 * fw)
            pieces.append(CutPiece(
                mullion_profile.profile_code, mullion_profile.profile_name,
                'Mullion', mullion_len, qty * (panels - 1), '90deg',
                mullion_profile.cost_per_meter
            ))

        # Glazing beads
        if bead_profile and dt != 'fixed_window':
            for i in range(panels):
                if dt in ('sliding_window', 'sliding_door'):
                    gw = int((W - (2 * fw)) / panels) - (2 * rd)
                    gh = (H - (2 * fw) - self.DEFAULT_TRACK_HEIGHT) - (2 * rd)
                else:
                    gw = int((W - (2 * fw) - (max(panels-1,0)*sw)) / panels) - (2 * rd)
                    gh = (H - (2 * fw)) - (2 * rd)
                bead_len_h = max(gw, 0)
                bead_len_v = max(gh, 0)
                pieces.append(CutPiece(bead_profile.profile_code, bead_profile.profile_name,
                    f'Bead Horizontal P{i+1}', bead_len_h, qty * 2, '45deg', bead_profile.cost_per_meter))
                pieces.append(CutPiece(bead_profile.profile_code, bead_profile.profile_name,
                    f'Bead Vertical P{i+1}', bead_len_v, qty * 2, '45deg', bead_profile.cost_per_meter))
        elif bead_profile and dt == 'fixed_window':
            gw = W - (2 * fw) - (2 * rd)
            gh = H - (2 * fw) - (2 * rd)
            pieces.append(CutPiece(bead_profile.profile_code, bead_profile.profile_name,
                'Bead Horizontal', max(gw, 0), qty * 2, '45deg', bead_profile.cost_per_meter))
            pieces.append(CutPiece(bead_profile.profile_code, bead_profile.profile_name,
                'Bead Vertical', max(gh, 0), qty * 2, '45deg', bead_profile.cost_per_meter))

        return pieces

    def _calculate_glass(self, design, glass_types, fw, rd, gap):
        """Calculate glass panel sizes."""
        W = design.width_mm
        H = design.height_mm
        panels = design.num_panels
        dt = design.design_type
        qty = design.quantity

        pieces = []

        if dt == 'fixed_window':
            gw = W - (2 * fw) - (2 * rd) - gap
            gh = H - (2 * fw) - (2 * rd) - gap
            pieces.append(GlassPiece('Fixed Panel Glass', max(gw,0), max(gh,0),
                design.glass_type, design.glass_thickness_mm, qty))

        elif dt in ('sliding_window', 'sliding_door'):
            panel_w = int((W - (2 * fw)) / panels)
            gw = panel_w - (2 * rd) - gap
            if dt == 'sliding_window':
                gh = H - (2 * fw) - self.DEFAULT_TRACK_HEIGHT - (2 * rd) - gap
            else:
                gh = H - fw - self.DEFAULT_TRACK_HEIGHT - (2 * rd) - gap
            for i in range(panels):
                pieces.append(GlassPiece(f'Panel {i+1} Glass', max(gw,0), max(gh,0),
                    design.glass_type, design.glass_thickness_mm, qty))

        else:  # casement, french, bi-fold, tilt-turn
            sw = self.DEFAULT_SASH_WALL
            sash_w = int((W - (2*fw) - (max(panels-1,0)*sw)) / panels)
            gw = sash_w - (2 * rd) - gap
            gh = H - (2 * fw) - (2 * rd) - gap
            for i in range(panels):
                pieces.append(GlassPiece(f'Leaf {i+1} Glass', max(gw,0), max(gh,0),
                    design.glass_type, design.glass_thickness_mm, qty))

        return pieces

    def _calculate_hardware(self, design, hardware_items):
        """Calculate hardware bill of quantities."""
        dt = design.design_type
        panels = design.num_panels
        qty = design.quantity
        boq = []

        for hw in hardware_items:
            if dt not in hw.applies_to_types:
                continue
            formula = hw.quantity_formula or '1_per_unit'
            if formula == '1_per_unit':
                hw_qty = 1 * qty
            elif formula == '2_per_sash':
                hw_qty = 2 * panels * qty
            elif formula == '1_per_sash':
                hw_qty = panels * qty
            elif formula == '3_per_sash':
                hw_qty = 3 * panels * qty
            elif formula == 'perimeter_m':
                perim = 2 * (design.width_mm + design.height_mm) / 1000
                hw_qty = int(perim * qty) + 1
            elif formula == '1_per_panel':
                hw_qty = panels * qty
            else:
                hw_qty = 1 * qty

            boq.append(HardwareBOQItem(
                code=hw.code, name=hw.name, category=hw.category,
                unit=hw.unit, quantity=hw_qty, cost_per_unit=hw.cost_per_unit
            ))
        return boq

    def _optimize_bars(self, cut_pieces, profiles, kerf=3):
        """
        Apply First Fit Decreasing bin-packing algorithm.
        Groups pieces by profile code and optimizes cutting from standard bars.
        """
        from collections import defaultdict

        grouped = defaultdict(list)
        for piece in cut_pieces:
            for _ in range(piece.quantity):
                grouped[piece.profile_code].append({
                    'description': piece.description,
                    'length': piece.length_mm,
                })

        results = []
        for p_code, pieces_list in grouped.items():
            profile = profiles.filter(profile_code=p_code).first()
            bar_len = profile.standard_bar_length_mm if profile else 6000
            p_name = profile.profile_name if profile else p_code

            sorted_pieces = sorted(pieces_list, key=lambda x: x['length'], reverse=True)
            bars = []

            for piece in sorted_pieces:
                placed = False
                for bar in bars:
                    remaining = bar_len - sum(c['length'] + kerf for c in bar)
                    if remaining >= piece['length']:
                        bar.append({'length': piece['length'], 'desc': piece['description'], 'kerf': kerf})
                        placed = True
                        break
                if not placed:
                    bars.append([{'length': piece['length'], 'desc': piece['description'], 'kerf': kerf}])

            bar_cuts = []
            total_waste = 0
            for idx, bar in enumerate(bars):
                used = sum(c['length'] + c['kerf'] for c in bar)
                waste = bar_len - used
                total_waste += waste
                bar_cuts.append({
                    'bar_number': idx + 1,
                    'cuts': [{'length': c['length'], 'desc': c['desc']} for c in bar],
                    'used_mm': used,
                    'waste_mm': max(waste, 0),
                    'bar_length_mm': bar_len,
                })

            total_material = len(bars) * bar_len
            wp = round(total_waste / total_material * 100, 1) if total_material > 0 else 0

            opt = OptimizationResult(
                profile_code=p_code, profile_name=p_name,
                bars=bar_cuts, total_bars=len(bars),
                total_waste_mm=total_waste, waste_percent=wp,
                bar_length_mm=bar_len
            )
            results.append(opt)

        return results

    def _calculate_costs(self, cut_pieces, glass_pieces, hardware_items, bar_opts,
                         design, glass_types, pricing_config):
        """Calculate complete cost breakdown."""
        pc = pricing_config
        profile_markup = (Decimal('100') + pc.profile_markup_percent) / Decimal('100')
        glass_markup = (Decimal('100') + pc.glass_markup_percent) / Decimal('100')
        hw_markup = (Decimal('100') + pc.hardware_markup_percent) / Decimal('100')

        profile_cost = sum(p.cost for p in cut_pieces) * profile_markup
        glass_cost = Decimal('0')
        for gp in glass_pieces:
            gt = glass_types.filter(category=gp.glass_type).first()
            price = gt.price_per_sqm if gt else Decimal('500')
            glass_cost += gp.total_area_sqm * price
        glass_cost *= glass_markup

        hardware_cost = sum(h.total_cost for h in hardware_items) * hw_markup
        labour_cost = pc.labour_cost_per_unit * design.quantity
        base = profile_cost + glass_cost + hardware_cost + labour_cost
        overhead = base * pc.overhead_percent / Decimal('100')
        subtotal = base + overhead
        tax = subtotal * pc.tax_rate_percent / Decimal('100')
        total = subtotal + tax

        return {
            'profile_cost': str(profile_cost.quantize(Decimal('0.01'))),
            'glass_cost': str(glass_cost.quantize(Decimal('0.01'))),
            'hardware_cost': str(hardware_cost.quantize(Decimal('0.01'))),
            'labour_cost': str(labour_cost.quantize(Decimal('0.01'))),
            'overhead': str(overhead.quantize(Decimal('0.01'))),
            'subtotal': str(subtotal.quantize(Decimal('0.01'))),
            'tax_amount': str(tax.quantize(Decimal('0.01'))),
            'tax_rate': str(pc.tax_rate_percent),
            'total': str(total.quantize(Decimal('0.01'))),
            'currency': pc.currency_symbol,
        }

    # Serialization helpers
    def _piece_to_dict(self, p):
        return {'profile_code': p.profile_code, 'profile_name': p.profile_name,
                'description': p.description, 'length_mm': p.length_mm,
                'quantity': p.quantity, 'cut_angle': p.cut_angle,
                'cost_per_meter': str(p.cost_per_meter), 'total_cost': str(p.cost)}

    def _glass_to_dict(self, g):
        return {'description': g.description, 'width_mm': g.width_mm, 'height_mm': g.height_mm,
                'glass_type': g.glass_type, 'thickness_mm': g.thickness_mm,
                'quantity': g.quantity, 'area_sqm': str(g.area_sqm),
                'total_area_sqm': str(g.total_area_sqm)}

    def _hw_to_dict(self, h):
        return {'code': h.code, 'name': h.name, 'category': h.category,
                'unit': h.unit, 'quantity': h.quantity,
                'cost_per_unit': str(h.cost_per_unit), 'total_cost': str(h.total_cost)}

    def _opt_to_dict(self, o):
        return {'profile_code': o.profile_code, 'profile_name': o.profile_name,
                'bars': o.bars, 'total_bars': o.total_bars,
                'total_waste_mm': o.total_waste_mm, 'waste_percent': o.waste_percent,
                'bar_length_mm': o.bar_length_mm}
