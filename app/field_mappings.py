"""
Field mappings for the Insurance Fraud Detection form.
Maps human-readable dropdown values to their LabelEncoder integer codes.
LabelEncoder assigns integers in alphabetical sort order.
"""

# The exact order of features the model expects (PolicyNumber REMOVED)
FEATURE_ORDER = [
    'WeekOfMonth', 'Make', 'AccidentArea', 'DayOfWeekClaimed',
    'WeekOfMonthClaimed', 'Sex', 'MaritalStatus', 'Age', 'Fault',
    'PolicyType', 'VehicleCategory', 'VehiclePrice', 'Deductible',
    'Days_Policy_Accident', 'Days_Policy_Claim', 'PastNumberOfClaims',
    'AgeOfVehicle', 'AgeOfPolicyHolder', 'PoliceReportFiled',
    'WitnessPresent', 'AgentType', 'NumberOfSuppliments',
    'AddressChange_Claim', 'NumberOfCars', 'BasePolicy'
]

# Numeric fields that pass through without encoding
NUMERIC_FIELDS = {'WeekOfMonth', 'WeekOfMonthClaimed', 'Age', 'Deductible'}

# Label encoding mappings: string -> integer (alphabetical order)
LABEL_ENCODINGS = {
    'Make': {
        'Accura': 0, 'BMW': 1, 'Chevrolet': 2, 'Dodge': 3, 'Ferrari': 4,
        'Ford': 5, 'Honda': 6, 'Jaguar': 7, 'Lexus': 8, 'Mazda': 9,
        'Mecedes': 10, 'Mercury': 11, 'Nisson': 12, 'Pontiac': 13,
        'Porche': 14, 'Saab': 15, 'Saturn': 16, 'Toyota': 17, 'VW': 18
    },
    'AccidentArea': {'Rural': 0, 'Urban': 1},
    'DayOfWeekClaimed': {
        'Friday': 0, 'Monday': 1, 'Saturday': 2, 'Sunday': 3,
        'Thursday': 4, 'Tuesday': 5, 'Wednesday': 6
    },
    'Sex': {'Female': 0, 'Male': 1},
    'MaritalStatus': {'Divorced': 0, 'Married': 1, 'Single': 2, 'Widow': 3},
    'Fault': {'Policy Holder': 0, 'Third Party': 1},
    'PolicyType': {
        'Sedan - All Perils': 0, 'Sedan - Collision': 1, 'Sedan - Liability': 2,
        'Sport - All Perils': 3, 'Sport - Collision': 4, 'Sport - Liability': 5,
        'Utility - All Perils': 6, 'Utility - Collision': 7, 'Utility - Liability': 8
    },
    'VehicleCategory': {'Sedan': 0, 'Sport': 1, 'Utility': 2},
    'VehiclePrice': {
        '20000 to 29000': 0, '30000 to 39000': 1, '40000 to 59000': 2,
        '60000 to 69000': 3, 'less than 20000': 4, 'more than 69000': 5
    },
    'Days_Policy_Accident': {
        '1 to 7': 0, '15 to 30': 1, '8 to 15': 2, 'more than 30': 3, 'none': 4
    },
    'Days_Policy_Claim': {
        '15 to 30': 0, '8 to 15': 1, 'more than 30': 2, 'none': 3
    },
    'PastNumberOfClaims': {
        '1': 0, '2 to 4': 1, 'more than 4': 2, 'none': 3
    },
    'AgeOfVehicle': {
        '2 years': 0, '3 years': 1, '4 years': 2, '5 years': 3,
        '6 years': 4, '7 years': 5, 'more than 7': 6, 'new': 7
    },
    'AgeOfPolicyHolder': {
        '16 to 17': 0, '18 to 20': 1, '21 to 25': 2, '26 to 30': 3,
        '31 to 35': 4, '36 to 40': 5, '41 to 50': 6, '51 to 65': 7, 'over 65': 8
    },
    'PoliceReportFiled': {'No': 0, 'Yes': 1},
    'WitnessPresent': {'No': 0, 'Yes': 1},
    'AgentType': {'External': 0, 'Internal': 1},
    'NumberOfSuppliments': {
        '1 to 2': 0, '3 to 5': 1, 'more than 5': 2, 'none': 3
    },
    'AddressChange_Claim': {
        '1 year': 0, '2 to 3 years': 1, '4 to 8 years': 2,
        'no change': 3, 'under 6 months': 4
    },
    'NumberOfCars': {
        '1 vehicle': 0, '2 vehicles': 1, '3 to 4': 2, '5 to 8': 3, 'more than 8': 4
    },
    'BasePolicy': {'All Perils': 0, 'Collision': 1, 'Liability': 2}
}

# Human-friendly labels and dropdown choices for the form
FIELD_CHOICES = {
    'WeekOfMonth': {
        'label': 'Week of Month',
        'choices': [('', 'Select...'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    },
    'Make': {
        'label': 'Vehicle Manufacturer',
        'choices': [('', 'Select...')] + [(k, k) for k in sorted(LABEL_ENCODINGS['Make'].keys())]
    },
    'AccidentArea': {
        'label': 'Accident Area',
        'choices': [('', 'Select...'), ('Rural', 'Rural'), ('Urban', 'Urban')]
    },
    'DayOfWeekClaimed': {
        'label': 'Day of Week Claimed',
        'choices': [('', 'Select...')] + [(d, d) for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    },
    'WeekOfMonthClaimed': {
        'label': 'Week of Month Claimed',
        'choices': [('', 'Select...'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    },
    'Sex': {
        'label': 'Gender',
        'choices': [('', 'Select...'), ('Female', 'Female'), ('Male', 'Male')]
    },
    'MaritalStatus': {
        'label': 'Marital Status',
        'choices': [('', 'Select...'), ('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widow', 'Widow')]
    },
    'Age': {
        'label': 'Age',
        'choices': None  # Numeric input
    },
    'Fault': {
        'label': 'Fault Attribution',
        'choices': [('', 'Select...'), ('Policy Holder', 'Policy Holder'), ('Third Party', 'Third Party')]
    },
    'PolicyType': {
        'label': 'Policy Type',
        'choices': [('', 'Select...')] + [(k, k) for k in sorted(LABEL_ENCODINGS['PolicyType'].keys())]
    },
    'VehicleCategory': {
        'label': 'Vehicle Category',
        'choices': [('', 'Select...'), ('Sedan', 'Sedan'), ('Sport', 'Sport'), ('Utility', 'Utility')]
    },
    'VehiclePrice': {
        'label': 'Vehicle Price Range',
        'choices': [('', 'Select...'), ('less than 20000', 'Less than \u20b920,000'), ('20000 to 29000', '\u20b920,000 - \u20b929,000'), ('30000 to 39000', '\u20b930,000 - \u20b939,000'), ('40000 to 59000', '\u20b940,000 - \u20b959,000'), ('60000 to 69000', '\u20b960,000 - \u20b969,000'), ('more than 69000', 'More than \u20b969,000')]
    },
    'Deductible': {
        'label': 'Deductible Amount',
        'choices': [('', 'Select...'), ('300', '\u20b9300'), ('400', '\u20b9400'), ('500', '\u20b9500'), ('700', '\u20b9700')]
    },
    'Days_Policy_Accident': {
        'label': 'Days: Policy to Accident',
        'choices': [('', 'Select...'), ('1 to 7', '1 to 7 days'), ('8 to 15', '8 to 15 days'), ('15 to 30', '15 to 30 days'), ('more than 30', 'More than 30 days'), ('none', 'None')]
    },
    'Days_Policy_Claim': {
        'label': 'Days: Policy to Claim',
        'choices': [('', 'Select...'), ('8 to 15', '8 to 15 days'), ('15 to 30', '15 to 30 days'), ('more than 30', 'More than 30 days'), ('none', 'None')]
    },
    'PastNumberOfClaims': {
        'label': 'Past Number of Claims',
        'choices': [('', 'Select...'), ('none', 'None'), ('1', '1'), ('2 to 4', '2 to 4'), ('more than 4', 'More than 4')]
    },
    'AgeOfVehicle': {
        'label': 'Age of Vehicle',
        'choices': [('', 'Select...'), ('new', 'New'), ('2 years', '2 years'), ('3 years', '3 years'), ('4 years', '4 years'), ('5 years', '5 years'), ('6 years', '6 years'), ('7 years', '7 years'), ('more than 7', 'More than 7 years')]
    },
    'AgeOfPolicyHolder': {
        'label': 'Age Group of Policy Holder',
        'choices': [('', 'Select...'), ('16 to 17', '16-17'), ('18 to 20', '18-20'), ('21 to 25', '21-25'), ('26 to 30', '26-30'), ('31 to 35', '31-35'), ('36 to 40', '36-40'), ('41 to 50', '41-50'), ('51 to 65', '51-65'), ('over 65', 'Over 65')]
    },
    'PoliceReportFiled': {
        'label': 'Police Report Filed',
        'choices': [('', 'Select...'), ('No', 'No'), ('Yes', 'Yes')]
    },
    'WitnessPresent': {
        'label': 'Witness Present',
        'choices': [('', 'Select...'), ('No', 'No'), ('Yes', 'Yes')]
    },
    'AgentType': {
        'label': 'Agent Type',
        'choices': [('', 'Select...'), ('External', 'External'), ('Internal', 'Internal')]
    },
    'NumberOfSuppliments': {
        'label': 'Number of Supplements',
        'choices': [('', 'Select...'), ('none', 'None'), ('1 to 2', '1 to 2'), ('3 to 5', '3 to 5'), ('more than 5', 'More than 5')]
    },
    'AddressChange_Claim': {
        'label': 'Address Change Since Claim',
        'choices': [('', 'Select...'), ('under 6 months', 'Under 6 months'), ('1 year', '1 year'), ('2 to 3 years', '2 to 3 years'), ('4 to 8 years', '4 to 8 years'), ('no change', 'No change')]
    },
    'NumberOfCars': {
        'label': 'Number of Cars',
        'choices': [('', 'Select...'), ('1 vehicle', '1 vehicle'), ('2 vehicles', '2 vehicles'), ('3 to 4', '3 to 4'), ('5 to 8', '5 to 8'), ('more than 8', 'More than 8')]
    },
    'BasePolicy': {
        'label': 'Base Policy',
        'choices': [('', 'Select...'), ('All Perils', 'All Perils'), ('Collision', 'Collision'), ('Liability', 'Liability')]
    },
    'PolicyNumber': {
        'label': 'Policy Number',
        'choices': None  # Free text input
    }
}

# Wizard steps grouping
WIZARD_STEPS = [
    {
        'title': 'Policy Information',
        'description': 'Enter the insurance policy details',
        'icon': 'bi-file-earmark-text',
        'fields': ['PolicyNumber', 'WeekOfMonth', 'PolicyType', 'BasePolicy', 'Deductible', 'Days_Policy_Accident', 'Days_Policy_Claim', 'AgentType']
    },
    {
        'title': 'Personal Information',
        'description': 'Enter the policy holder details',
        'icon': 'bi-person',
        'fields': ['Sex', 'MaritalStatus', 'Age', 'AgeOfPolicyHolder', 'Fault', 'PastNumberOfClaims', 'AddressChange_Claim']
    },
    {
        'title': 'Vehicle & Accident',
        'description': 'Enter vehicle and accident details',
        'icon': 'bi-car-front',
        'fields': ['Make', 'VehicleCategory', 'VehiclePrice', 'AgeOfVehicle', 'AccidentArea', 'NumberOfCars']
    },
    {
        'title': 'Claim Details',
        'description': 'Enter the claim information',
        'icon': 'bi-clipboard-check',
        'fields': ['DayOfWeekClaimed', 'WeekOfMonthClaimed', 'PoliceReportFiled', 'WitnessPresent', 'NumberOfSuppliments']
    }
]
