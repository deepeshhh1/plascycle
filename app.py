from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from werkzeug.utils import safe_join
import os

# NOTE: Matplotlib is REMOVED for guaranteed stability in your local environment.

app = Flask(__name__)
CORS(app)

# Serve index.html securely
@app.route('/')
def serve_index():
    index_path = safe_join(os.path.dirname(__file__), 'index.html')
    if not os.path.exists(index_path):
        abort(404, description="index.html not found")
    return send_file(index_path)

def calculate_materials(aluminum_wrappers, normal_wrappers, thickness):
    """
    Calculate required materials and sheets possible.
    Returns: (material_text, required_wrappers, used_aluminum, used_normal, sheets_text, paint_liters)
    """
    base_kg = 8  # Base for 12mm Plywood (6x4 inches)
    thickness_factor = thickness / 12
    required_wrappers = base_kg * thickness_factor

    aluminum_needed = required_wrappers * 0.6
    normal_needed = required_wrappers * 0.4

    aluminum_available = float(aluminum_wrappers)
    normal_available = float(normal_wrappers)

    sheets_possible = min(aluminum_available // aluminum_needed, normal_available // normal_needed)

    if sheets_possible < 1:
        return (
            f"Insufficient materials! Need ≥ {aluminum_needed:.2f} kg aluminum & {normal_needed:.2f} kg normal wrappers for one sheet.",
            0, 0, 0, 0, 0
        )

    used_aluminum = aluminum_needed * sheets_possible
    used_normal = normal_needed * sheets_possible
    paint_liters = used_normal * 0.05

    sheets_text = f"<strong>You can build {sheets_possible:.0f} Plywood Sheet(s)</strong> (6x4 inches, {thickness}mm thick)."
    material_text = (
        f"<strong>Total Wrappers Used: {used_aluminum + used_normal:.2f} kg</strong><br>"
        f"- Aluminum Wrappers Used: {used_aluminum:.2f} kg<br>"
        f"- Non-Aluminum Wrappers Used: {used_normal:.2f} kg<br>"
        f"- PU Enamel Paint Required: {paint_liters:.2f} liters<br>"
        f"- Mold Size: 6x4 inches"
    )
    return material_text, required_wrappers, used_aluminum, used_normal, sheets_text, paint_liters

def generate_process(used_aluminum, used_normal, thickness, paint_liters):
    """
    Generate HTML process steps (Flow Chart and Detailed Steps).
    """
    sheets_type = "plywood sheet" if thickness <= 12 else "premium panel"
    
    # --- 1. Visible Flow Chart Section (5 simplified steps with images) ---
    simplified_steps = [
        {"name": "Washing", "img": "/static/assets/process/step1_washing.jpg"},
        {"name": "Cutting", "img": "/static/assets/process/step2_cutting.jpg"},
        {"name": "Segregation", "img": "/static/assets/process/step3_segregation.jpg"},
        {"name": "Melting", "img": "/static/assets/process/step4_melting.jpg"},
        {"name": "Molding", "img": "/static/assets/process/step5_molding.jpg"},
    ]
    
    # HTML for the 5-step Flow Chart
    flow_chart_html = f"""
    <h4 style="color:#3da35d; margin-top:16px;">Manufacturing Flow Chart</h4>
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:nowrap; gap:10px; margin-bottom: 20px;">
    """
    
    for i, step in enumerate(simplified_steps):
        flow_chart_html += f"""
        <div class="flow-step-box" style="background: #c6e9d4; padding: 10px; border-radius: 8px; flex-shrink: 0; min-width: 15%;">
            <img src="{step['img']}" alt="{step['name']}" onerror="this.onerror=null;this.src='/static/placeholder.jpg';" style="width: 100%; height: 50px; object-fit: cover; border-radius: 4px; display: block; margin-bottom: 5px;">
            <p style="color: black; margin: 0; font-weight: 600; font-size: 13px;">{step['name']}</p>
        </div>
        """
        if i < len(simplified_steps) - 1:
            flow_chart_html += f"""
            <span style="font-size: 20px; color: #4c92bf; margin: 0 5px; flex-shrink: 0;">&#8594;</span>
            """
            
    flow_chart_html += "</div>"
    
    
    # --- 2. Native <details> Toggle for Detailed 9-Step Process (The RELIABLE toggle) ---
    
    toggle_start = '<details class="detail-toggle">'
    summary_html = '<summary>Show Detailed Manufacturing Steps (9-Steps)</summary>'
    
    process_steps_data = [
        {"text": f"Collect and verify <b>{used_aluminum + used_normal:.2f} kg</b> of sorted wrappers."},
        {"text": "Sort, clean and shred wrappers using our <b>AI-Vision System</b>."},
        {"text": f"Roast <b>{used_aluminum:.2f} kg</b> aluminum wrappers at 240°C for 1 minute for bonding."},
        {"text": f"Mix with <b>{used_normal:.2f} kg</b> non-aluminum wrappers and chemical binder."},
        {"text": "Melt the mixture at 180°C for 3 minutes to form a polymer paste."},
        {"text": "Pour into 6x4 inch mold and compress under <b>50 tons of pressure</b>."},
        {"text": "Cool for 2 hours."},
        {"text": f"Sand surface for precise <b>{thickness} mm</b> thickness for the {sheets_type}."},
        {"text": f"Apply <b>{paint_liters:.2f} liters</b> PU enamel paint for water resistance."}
    ]
    
    html_steps = [f"<h4 style='color:#3da35d; margin-top:24px; padding-top:16px;'>Detailed Manufacturing Steps (9-Steps)</h4>"]
    for i, step in enumerate(process_steps_data):
        html_step = f"""
        <div class="step">
            <div class="step-content">
                <h3>Step {i+1}</h3>
                <p>{step['text']}</p>
            </div>
        </div>
        """
        html_steps.append(html_step)
        
    detailed_steps_html = "<div class='timeline'>" + "".join(html_steps) + "</div>"
    
    toggle_end = '</details>'

    return flow_chart_html + toggle_start + summary_html + detailed_steps_html + toggle_end


def ai_prediction(used_aluminum, used_normal, thickness):
    """
    Simulate ML/AI-based product prediction.
    """
    durability_map = {6: "Medium", 12: "High", 18: "Very High"}
    durability = durability_map.get(thickness, "Medium")
    aluminum_ratio = used_aluminum / used_normal if used_normal > 0 else 100

    if thickness >= 12 and aluminum_ratio >= 1.4:
        product_choice = "Premium Furniture Panel"
    elif thickness >= 12:
        product_choice = "Standard Plywood"
    else:
        product_choice = "Tile / Lightweight Furniture"

    cost_saving = round((used_aluminum + used_normal) * 1.5 + (thickness * 0.5), 2)
    return {
        "bestProduct": product_choice,
        "durability": durability,
        "costSaving": f"ML Analysis: Estimated ₹{cost_saving} saved compared to market wood"
    }

def generate_chart_info(used_aluminum, used_normal):
    """
    Generates text/HTML summary for the chart area instead of a graphic.
    """
    total = used_aluminum + used_normal
    aluminum_percent = (used_aluminum / total) * 100 if total > 0 else 0
    normal_percent = (used_normal / total) * 100 if total > 0 else 0
    
    chart_info_html = (
        f"<h4 style='color: #4c92bf;'>Wrapper Composition Summary</h4>"
        f"<p style='margin: 5px 0;'>&bull; Aluminum-backed: <strong>{aluminum_percent:.1f}%</strong> ({used_aluminum:.2f} kg)</p>"
        f"<p style='margin: 5px 0;'>&bull; Non-Aluminum: <strong>{normal_percent:.1f}%</strong> ({used_normal:.2f} kg)</p>"
        f"<div style='height: 10px; background: linear-gradient(to right, #28a745 {aluminum_percent}%, #444444 {aluminum_percent}%) ; border-radius: 5px; margin-top: 10px;'></div>"
    )
    # Returns an empty string for the chart image data
    return chart_info_html, ""

def estimate_trees_saved(used_aluminum, used_normal):
    """
    Estimate number of trees saved.
    Assume 1 tree yields about 50 kg of usable wood.
    """
    total_kg = used_aluminum + used_normal
    trees_saved = total_kg / 50
    return max(0, round(trees_saved, 2))

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json(force=True)
    aluminum_wrappers = data.get('aluminumWrappers')
    normal_wrappers = data.get('normalWrappers')
    thickness = data.get('thickness')

    if aluminum_wrappers is None or normal_wrappers is None or thickness is None:
        return jsonify({'error': 'Please fill all values!'}), 400

    try:
        aluminum_wrappers = float(aluminum_wrappers)
        normal_wrappers = float(normal_wrappers)
        thickness = float(thickness)
        if aluminum_wrappers < 0 or normal_wrappers < 0 or thickness <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numbers entered!'}), 400

    materials, required_wrappers, used_aluminum, used_normal, sheets, paint_liters = calculate_materials(
        aluminum_wrappers, normal_wrappers, thickness
    )

    if "Insufficient" in materials:
        return jsonify({'error': materials}), 400

    process = generate_process(used_aluminum, used_normal, thickness, paint_liters)
    ai_result = ai_prediction(used_aluminum, used_normal, thickness)
    chart_html, chart_base64 = generate_chart_info(used_aluminum, used_normal) 
    trees_saved = estimate_trees_saved(used_aluminum, used_normal)

    return jsonify({
        'sheets': sheets,
        'materials': materials,
        'process': process,
        'aiResult': ai_result,
        'chart': chart_base64, 
        'chartHtml': chart_html,
        'treesSaved': trees_saved
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': str(e)}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)