import os
import re

def update_file(path):
    if not os.path.exists(path): return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Import replacement
    content = content.replace("import { ToastrService } from 'ngx-toastr';", "import { HotToastService } from '@ngneat/hot-toast';")
    
    # Dependency injection replacements
    content = content.replace("private toastrservice: ToastrService", "private toastrservice: HotToastService")
    content = content.replace("private toastr: ToastrService", "private toastr: HotToastService")
    content = content.replace("private toster: ToastrService", "private toster: HotToastService")
    
    # Remove { toastClass: '...' } 
    content = re.sub(r",\s*\{\s*toastClass:\s*'[^']+'\s*\}\s*", '', content)
    
    # Remove extraneous arguments (Title strings) and objects { enableHtml: true, timeOut: 5000 }
    # Let's just do targeted replaces for the known problematic lines shown in the errors
    content = content.replace(", 'Error'", "")
    content = content.replace(",\n          'Email Sent'", "")
    content = content.replace(",\n          'Nothing to Send'", "")
    content = content.replace(",\n          'Send Failed'", "")
    content = content.replace(",\n        ''", "")
    content = content.replace(", { enableHtml: true, timeOut: 5000 }", "")
    content = content.replace(", { timeOut: 5000 }", "")

    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

files = [
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\Admin\validation-timesheet\validation-timesheet.component.ts",
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\Admin\user-timesheets-list\user-timesheets-list.component.ts",
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\Admin\project-members\project-members.component.ts",
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\Admin\ppt-automation\ppt-automation.component.ts",
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\shared\notification-center\notification-center.component.ts",
    r"d:\entrans-hr-hub-fullstasck\entrans-hr-hub\timesheetManagement\src\app\Admin\analytics-dashboard\analytics-dashboard.component.ts"
]

for f in files:
    update_file(f)
print("Done updating files again")
