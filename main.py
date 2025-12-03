from flask import Flask, request, jsonify
from lambda_generator import generate_lambda_project
import json
import os

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['lambdaFolderName', 'lambdaName', 'inputSchema', 'outputSchema']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        lambda_folder_name = data['lambdaFolderName'].strip()
        lambda_name = data['lambdaName'].strip()
        if not lambda_folder_name or not lambda_name:
            return jsonify({'error': 'lambdaFolderName and lambdaName cannot be empty'}), 400

        try:
            input_schema = json.loads(data['inputSchema'])
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in inputSchema'}), 400

        try:
            output_schema = json.loads(data['outputSchema'])
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in outputSchema'}), 400

        field_mapping = {}
        if data.get('mappingDoc'):
            try:
                field_mapping = json.loads(data['mappingDoc'])
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON in mappingDoc'}), 400

        required_fields_list = []
        if data.get('requiredFields'):
            required_fields_list = [f.strip() for f in data['requiredFields'].split(',') if f.strip()]

        env_vars = data.get('envVars', {})

        # CDK Configuration
        memory_size = data.get('memorySize', 300)
        route_type = data.get('routeType', 'compData_product')
        source_interface_name = data.get('sourceInterfaceName', '').strip()
        target_interface_name = data.get('targetInterfaceName', '').strip()
        interface_type = data.get('interfaceType', 'consumer')

        base_dir = data.get('location', os.path.join(os.path.expanduser('~'), 'Desktop')).strip() or os.path.join(os.path.expanduser('~'), 'Desktop')

        generate_lambda_project(
            lambda_folder_name=lambda_folder_name,
            lambda_name=lambda_name,
            input_schema=input_schema,
            output_schema=output_schema,
            required_fields=required_fields_list,
            field_mapping=field_mapping,
            base_dir=base_dir,
            api_url=data.get('apiUrl', '').strip() or None,
            env_vars=env_vars,
            memory_size=memory_size,
            route_type=route_type,
            source_interface_name=source_interface_name,
            target_interface_name=target_interface_name,
            interface_type=interface_type,
        )

        return jsonify({'message': f'Lambda project {lambda_folder_name} generated successfully at {base_dir}'}), 200
    except Exception as e:
        app.logger.error(f'Error generating project: {str(e)}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
