"""Report generation views for FENESTRA PRO."""
import io
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from openpyxl import Workbook
from apps.designs.models import WindowDoorDesign
from apps.quotations.models import Quotation
from apps.pricing.models import PricingConfig


@login_required
def download_quotation_pdf(request, number):
    """Generate and download quotation as PDF."""
    quot = get_object_or_404(Quotation, quotation_number=number)
    if request.user.is_customer and quot.customer != request.user:
        return HttpResponse('Access denied', status=403)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20,
        textColor=colors.HexColor('#0D1117'), spaceAfter=10)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=12,
        textColor=colors.HexColor('#F0A500'), fontName='Helvetica-Bold', spaceAfter=5)
    normal = styles['Normal']
    elements = []
    elements.append(Paragraph('FENESTRA PRO', title_style))
    elements.append(Paragraph('Window & Door Fabrication Solutions', normal))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph(f'QUOTATION: {quot.quotation_number}', header_style))
    elements.append(Paragraph(f'Date: {quot.generated_at.strftime("%d-%b-%Y")}', normal))
    elements.append(Paragraph(f'Valid Until: {quot.valid_until}', normal))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(f'Customer: {quot.customer.company_name or quot.customer.get_full_name()}', normal))
    elements.append(Paragraph(f'Email: {quot.customer.email}', normal))
    elements.append(Spacer(1, 8*mm))
    # Line items table
    data = [['#', 'Description', 'Dimensions', 'Qty', 'Unit Price', 'Total']]
    config = PricingConfig.get_active()
    for idx, item in enumerate(quot.line_items, 1):
        data.append([str(idx), item['description'], item.get('dimensions',''),
                     str(item['quantity']), f"{config.currency_symbol}{item['unit_price']}",
                     f"{config.currency_symbol}{item['total']}"])
    data.append(['', '', '', '', 'Subtotal:', f"{config.currency_symbol}{quot.subtotal}"])
    data.append(['', '', '', '', f'Tax ({config.tax_rate_percent}%):', f"{config.currency_symbol}{quot.tax_amount}"])
    data.append(['', '', '', '', 'TOTAL:', f"{config.currency_symbol}{quot.total}"])
    table = Table(data, colWidths=[15*mm, 55*mm, 35*mm, 15*mm, 25*mm, 30*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1117')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-4), 0.5, colors.HexColor('#333333')),
        ('FONTNAME', (4,-3), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (4,-3), (-1,-3), 1, colors.HexColor('#F0A500')),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-4), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph('Terms & Conditions:', header_style))
    for line in quot.terms_conditions.split('\n'):
        elements.append(Paragraph(line.strip(), ParagraphStyle('TC', parent=normal, fontSize=8)))
    doc.build(elements)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{quot.quotation_number}.pdf"'
    return response


@login_required
def download_boq_pdf(request, code):
    """Generate BOQ PDF for a design."""
    design = get_object_or_404(WindowDoorDesign, code=code)
    calc = design.calculation_data or {}
    config = PricingConfig.get_active()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#0D1117'))
    head_s = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#F0A500'))
    elements = []
    elements.append(Paragraph('BILL OF QUANTITIES', title_s))
    elements.append(Paragraph(f'Design: {design.code} — {design.name}', styles['Normal']))
    elements.append(Spacer(1, 8*mm))
    # Section A: Profiles
    elements.append(Paragraph('Section A: Profile Materials', head_s))
    p_data = [['Profile Code', 'Description', 'Length (mm)', 'Qty', 'Cost/m', 'Total']]
    for p in calc.get('cut_pieces', []):
        p_data.append([p['profile_code'], p['description'], str(p['length_mm']),
                       str(p['quantity']), p['cost_per_meter'], f"{config.currency_symbol}{p['total_cost']}"])
    if len(p_data) > 1:
        t = Table(p_data, colWidths=[25*mm, 40*mm, 25*mm, 15*mm, 25*mm, 30*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 7), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 5*mm))
    # Section B: Glass
    elements.append(Paragraph('Section B: Glass', head_s))
    g_data = [['Description', 'Width', 'Height', 'Area (sqm)', 'Qty', 'Type']]
    for g in calc.get('glass_pieces', []):
        g_data.append([g['description'], str(g['width_mm']), str(g['height_mm']),
                       g['area_sqm'], str(g['quantity']), g['glass_type']])
    if len(g_data) > 1:
        t = Table(g_data, colWidths=[35*mm, 20*mm, 20*mm, 25*mm, 15*mm, 30*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 7), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 5*mm))
    # Section C: Hardware
    elements.append(Paragraph('Section C: Hardware & Accessories', head_s))
    h_data = [['Code', 'Name', 'Unit', 'Qty', 'Unit Cost', 'Total']]
    for h in calc.get('hardware_items', []):
        h_data.append([h['code'], h['name'], h['unit'], str(h['quantity']),
                       f"{config.currency_symbol}{h['cost_per_unit']}", f"{config.currency_symbol}{h['total_cost']}"])
    if len(h_data) > 1:
        t = Table(h_data, colWidths=[20*mm, 40*mm, 18*mm, 15*mm, 25*mm, 25*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 7), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 5*mm))
    # Cost summary
    cb = calc.get('cost_breakdown', {})
    elements.append(Paragraph('Cost Summary', head_s))
    for label, key in [('Profile Cost', 'profile_cost'), ('Glass Cost', 'glass_cost'),
                       ('Hardware Cost', 'hardware_cost'), ('Labour', 'labour_cost'),
                       ('Overhead', 'overhead'), ('Subtotal', 'subtotal'),
                       ('Tax', 'tax_amount'), ('GRAND TOTAL', 'total')]:
        val = cb.get(key, '0.00')
        elements.append(Paragraph(f'{label}: {config.currency_symbol}{val}', styles['Normal']))
    doc.build(elements)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BOQ-{design.code}.pdf"'
    return response


@login_required
def download_production_pdf(request, code):
    """Generate Production/Fabrication PDF for a design (Maker only)."""
    if not request.user.is_maker:
        return HttpResponse('Access denied', status=403)
        
    design = get_object_or_404(WindowDoorDesign, code=code)
    calc = design.calculation_data or {}
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#0D1117'))
    head_s = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#F0A500'))
    
    elements = []
    elements.append(Paragraph('PRODUCTION & CUTTING REPORT', title_s))
    elements.append(Paragraph(f'Design: {design.code} — {design.name}', styles['Normal']))
    elements.append(Spacer(1, 8*mm))
    
    # Section A: Profiles
    elements.append(Paragraph('Section A: Profile Materials', head_s))
    p_data = [['Profile Code', 'Description', 'Length (mm)', 'Qty', 'Angle']]
    for p in calc.get('cut_pieces', []):
        p_data.append([p['profile_code'], p['description'], str(p['length_mm']),
                       str(p['quantity']), p.get('cut_angle', '')])
    if len(p_data) > 1:
        t = Table(p_data, colWidths=[30*mm, 50*mm, 30*mm, 20*mm, 30*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 5*mm))
    
    # Section B: Glass
    elements.append(Paragraph('Section B: Glass Materials', head_s))
    g_data = [['Description', 'Width', 'Height', 'Area (sqm)', 'Qty', 'Type']]
    for g in calc.get('glass_pieces', []):
        g_data.append([g['description'], str(g['width_mm']), str(g['height_mm']),
                       str(g.get('area_sqm', '')), str(g['quantity']), g['glass_type']])
    if len(g_data) > 1:
        t = Table(g_data, colWidths=[40*mm, 20*mm, 20*mm, 25*mm, 20*mm, 35*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 5*mm))

    # Section C: Hardware
    elements.append(Paragraph('Section C: Hardware & Accessories', head_s))
    h_data = [['Code', 'Name', 'Unit', 'Qty']]
    for h in calc.get('hardware_items', []):
        h_data.append([h['code'], h['name'], h['unit'], str(h['quantity'])])
    if len(h_data) > 1:
        t = Table(h_data, colWidths=[30*mm, 70*mm, 30*mm, 30*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161B22')), ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
    elements.append(Spacer(1, 10*mm))
    
    # Section D: Bar Optimization
    elements.append(Paragraph('Section D: Bar Cutting Optimization (6m Bars)', head_s))
    opts = calc.get('bar_optimizations', [])
    if opts:
        for opt in opts:
            elements.append(Paragraph(f"<b>{opt['profile_name']}</b> - Total Bars: {opt['total_bars']} (Waste: {opt['waste_percent']}%)", styles['Normal']))
            for bar in opt['bars']:
                cut_str = " | ".join([f"{c['length']}mm" for c in bar['cuts']])
                elements.append(Paragraph(f"Bar #{bar['bar_number']}: {cut_str} (Waste: {bar['waste_mm']}mm)", ParagraphStyle('small', parent=styles['Normal'], fontSize=8)))
            elements.append(Spacer(1, 3*mm))
    else:
        elements.append(Paragraph('No bar optimization data available.', styles['Normal']))

    doc.build(elements)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Fabrication-{design.code}.pdf"'
    return response
