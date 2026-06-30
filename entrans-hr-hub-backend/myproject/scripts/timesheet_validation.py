import pandas as pd
import os
from dateutil.parser import parse
from datetime import datetime
import calendar
import zipfile
import shutil
import json
from collections import OrderedDict

class TimeValidator:
    '''Class for timesheet validation operations'''

    def __init__(self):
        self.results = []
        self.is_single_sheet = False

    def standardize_column_names(self, df):
        '''Standardize column names across different sheets.'''
        df = df.copy()
        for col in df.columns:
            if "Duration (in hrs)" in col or "Hours" in col:
                df.rename(columns={col: "Hours"}, inplace=True)

        if "Description" in df.columns:
            df.rename(columns={"Description": "Description"}, inplace=True)

        return df

    def validate(self, df):
        '''Validate timesheet data according to business rules.'''
        df = self.standardize_column_names(df)

        required_columns = ["Project", "Description", "Hours"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        df["Status"] = "Valid"
        df["Flag"] = ""

        for index, row in df.iterrows():
            client = str(row["Project"]).strip() if pd.notna(row["Project"]) else ""
            sheet_name = str(row["Description"]).strip() if pd.notna(row["Description"]) else ""
            hours = row["Hours"]

            is_leave_type = any(leave_type.lower() in client.lower() for leave_type in ["leave", "holiday", "weekend"])

            if is_leave_type:
                if pd.notna(hours) and hours != 0:
                    df.at[index, "Status"] = "Leave/Holiday should be 0 or empty"
                else:
                    df.at[index, "Status"] = "Valid"
            else:
                if pd.notna(hours):
                    if isinstance(hours, (int, float)):
                        if hours == 4:
                            df.at[index, "Status"] = "Half-day detected"
                            df.at[index, "Flag"] = "⚠ Half-Day Alert"
                        elif hours != 8:
                            df.at[index, "Status"] = f"Full working day should be 8 hrs, found {hours} hrs"
                    else:
                        df.at[index, "Status"] = "Invalid Hours Format"
                else:
                    df.at[index, "Status"] = "Missing hours for a working day"

        for index, row in df.iterrows():
            description = str(row["Description"]).strip() if pd.notna(row["Description"]) else ""
            if not description:
                df.at[index, "Flag"] += "⚠ Blank Description; "

        for index, row in df.iterrows():
            date_str = str(row["Date"])
            try:
                parsed_date = parse(date_str)
                df.at[index, "Date"] = parsed_date.strftime("%Y-%m-%d")
                if parsed_date.weekday() >= 5:  
                    if row["Hours"] not in [0, '0', 0.0, None, '']: 
                        df.at[index, "Status"] = "Timesheet filled on weekend"
                        df.at[index, "Flag"] += "⚠ Weekend Entry; "
            except Exception:
                df.at[index, "Date"] = None

        return df[["Project", "Date", "Description", "Hours", "Status", "Flag"]]

    def create_summary(self, validated_sheets):
        '''Create a summary sheet with serial numbers.'''
        summary_columns = ["S.No", "File Name", "Description", "Hours", "Review"]
        summary_data = []
        s_no = 1

        for sheet_name, df in validated_sheets.items():
            total_hours = df["Hours"].sum() if "Hours" in df.columns and df["Hours"].notna().any() else 0
            issues = []

            if any(df["Status"] == "Half-day detected"):
                issues.append("Contains half-days")

            non_standard_entries = df[df["Status"].str.contains("Full working day should be 8 hrs", na=False)]
            if not non_standard_entries.empty:
                issues.append("Has non-standard hours")

            if any(df["Status"] == "Leave/Holiday should be 0 or empty"):
                issues.append("Incorrectly logged leave/holiday")

            if any(df["Status"] == "Missing hours for a working day"):
                issues.append("Missing hours entries")

            if any(df["Status"] == "Invalid Hours Format"):
                issues.append("Invalid hour format")

            if any(df["Flag"].str.contains("Blank Description", na=False)):
                issues.append("Has blank descriptions")

            review_message = ", ".join(issues) if issues else "OK"

            summary_data.append({
                "S.No": s_no,
                "File Name": sheet_name,
                "Description": sheet_name,
                "Hours": total_hours,
                "Review": review_message
            })
            s_no += 1

        summary_df = pd.DataFrame(summary_data, columns=summary_columns)
        total_hours_row = pd.DataFrame([{'S.No': '', 'File Name': 'Total', 'Description': '', 'Hours': summary_df['Hours'].sum(), 'Review': ''}])
        summary_df = pd.concat([summary_df, total_hours_row], ignore_index=True)

        return summary_df

    def run(self, file_path):
        '''Run validation on all sheets in an Excel file.'''
        try:
            sheets_dict = pd.read_excel(file_path, sheet_name=None)
            is_single_sheet = len(sheets_dict) == 1
            validated_sheets = {}

            for sheet_name, df in sheets_dict.items():
                validated_sheets[sheet_name] = self.validate(df)
            file_name = os.path.basename(file_path)
            summary = self.create_summary(validated_sheets)
            summary["File Name"] = file_name
            result = {
                "file_path": file_path,
                "validated_sheets": validated_sheets,
                "summary": summary,
                "success": True,
                "is_single_sheet": is_single_sheet
            }

            self.results.append(result)
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_json(self, json_records):
        '''Validate JSON-based timesheet data (from GET API).'''
        try:
            if not isinstance(json_records, list):
                raise ValueError("Invalid input format. Expected a list of dicts.")

            df = pd.DataFrame(json_records)

            if df.empty:
                return {"success": False, "error": "Empty JSON data received."}

            validated_df = self.validate(df)
            validated_sheets = {"Sheet1": validated_df}
            summary_df = self.create_summary(validated_sheets)

            return {
                "success": True,
                "validated_sheets": validated_sheets,
                "summary": summary_df
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def validate_dataframe(self, df: pd.DataFrame) -> dict:
        '''Validate a single timesheet dataframe and return records and summary'''
        if df.empty:
            return {
                "success": False,
                "error": "Empty dataframe received.",
                "validated_data": [],
                "summary_data": []
            }

        validated_df = self.validate(df)
        validated_sheets = {"Sheet1": validated_df}
        summary_df = self.create_summary(validated_sheets)

        validated_records = validated_df.astype(str).to_dict(orient="records")
        summary_records = summary_df.astype(str).to_dict(orient="records")

        return {
            "success": True,
            "validated_data": validated_records,
            "summary_data": summary_records
        }

class OutputManager:
    """Class for handling output operations"""

    def __init__(self, output_dir, archive_dir, base_validation_dir):
        self.output_dir = output_dir
        self.archive_dir = archive_dir
        self.base_validation_dir = base_validation_dir
        self.current_validation_dir = None
        
        for directory in [output_dir, archive_dir, base_validation_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    def save_as_json(self, validation_result, validation_number=None):
        """Save single sheet validation results as JSON"""
        self.set_validation_directory(validation_number)
        
        file_name = os.path.basename(validation_result["file_path"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subfolder_name = f"validation_{timestamp}"
        subfolder_path = os.path.join(self.current_validation_dir, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        
        json_data = OrderedDict([
            ("summary", validation_result["summary"].to_dict(orient='records')),
            ("validated_data", list(validation_result["validated_sheets"].values())[0].to_dict(orient='records'))
        ])
        
        base_name = os.path.splitext(file_name)[0]
        json_filename = f"{base_name}_validation_{timestamp}.json"
        json_path = os.path.join(subfolder_path, json_filename)
        
        try:
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=4)
            return json_path
        except Exception as e:
            return None
        
    def set_validation_directory(self, validation_number=None):
        """Set the current validation directory to use.

        Args:
            validation_number: Integer or string to specify which validation folder to use
                               If None, uses the base validation directory
        """
        if validation_number is None:
            self.current_validation_dir = self.base_validation_dir
        else:
            validation_folder = f"validation{validation_number}"
            self.current_validation_dir = os.path.join(self.base_validation_dir, validation_folder)
        if not os.path.exists(self.current_validation_dir):
            os.makedirs(self.current_validation_dir)

        return self.current_validation_dir

    def get_summary_file_path(self):
        """Get the path to the summary file based on current validation directory"""
        if not self.current_validation_dir:
            self.set_validation_directory()

        if self.current_validation_dir == self.base_validation_dir:
            return os.path.join(self.current_validation_dir, "validation_summary.xlsx")
        else:
            folder_name = os.path.basename(self.current_validation_dir)
            return os.path.join(self.current_validation_dir, f"{folder_name}_summary.xlsx")

    def save_validated_data(self, validation_result, validation_number=None, output_path=None):
        """Save validated data in appropriate format based on sheet count"""
        if not validation_result.get("success", True):
            return None

        if validation_result.get("is_single_sheet", False):
            self.set_validation_directory(validation_number)
            
            file_name = os.path.basename(validation_result["file_path"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            subfolder_name = f"validation_{timestamp}"
            subfolder_path = os.path.join(self.current_validation_dir, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            validated_df = list(validation_result["validated_sheets"].values())[0]
        
            for col in validated_df.columns:
                if pd.api.types.is_datetime64_any_dtype(validated_df[col]):
                    validated_df[col] = validated_df[col].apply(
                        lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None
                    )
            json_data = {
                "summary": validation_result["summary"].to_dict(orient='records'),
                "validated_data": list(validation_result["validated_sheets"].values())[0].to_dict(orient='records')
            }
            
            base_name = os.path.splitext(file_name)[0]
            json_path = os.path.join(subfolder_path, f"{base_name}_validation_{timestamp}.json")
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=4)
            return json_path

        self.set_validation_directory(validation_number)
        file_name = os.path.basename(validation_result["file_path"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subfolder_name = f"validation_{timestamp}"
        subfolder_path = os.path.join(self.current_validation_dir, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        
        if output_path is None:
            output_name = f"validation_{timestamp}_{file_name}"
            output_path = os.path.join(subfolder_path, output_name)

        try:
            validated_sheets = validation_result["validated_sheets"]
            summary_df = validation_result["summary"]
            summary_path = os.path.join(subfolder_path, "validation_summary.xlsx")
            summary_df.to_excel(summary_path, index=False)

            with pd.ExcelWriter(output_path) as writer:
                for sheet, df in validated_sheets.items():
                    df.to_excel(writer, sheet_name=sheet, index=False)
            zip_path = self.create_zip_archive(output_path)
            self.add_to_summary_tracking(validation_result, validation_number)
            if validation_number is not None:
                self.add_to_master_summary(validation_result)
            return zip_path
        except Exception as e:
            return None

    def add_to_summary_tracking(self, validation_result, validation_number=None):
        """Add validation results to a summary tracking file in the specific validation directory."""
        self.set_validation_directory(validation_number)
        summary_path = self.get_summary_file_path()

        file_name = os.path.basename(validation_result["file_path"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(summary_path):
            try:
                summary_tracking = pd.read_excel(summary_path)
            except:
                summary_tracking = pd.DataFrame(columns=["S.No", "File Name", "Description", "Hours", "Review", "Validation Date"])
        else:
            summary_tracking = pd.DataFrame(columns=["S.No", "File Name", "Description", "Hours", "Review", "Validation Date"])

        new_entries = []

        start_sno = 1
        if not summary_tracking.empty and "S.No" in summary_tracking.columns:
            try:
                start_sno = summary_tracking["S.No"].max() + 1
            except:
                start_sno = 1
        sno = start_sno
        for sheet_name, df in validation_result["validated_sheets"].items():
            total_hours = 0
            if "Hours" in df.columns:
                total_hours = df["Hours"].sum()

            review_msg = ""
            if any(df["Status"] != "Valid"):
                issues = []
                if any(df["Status"] == "Half-day detected"):
                    issues.append("Contains half-days")
                if any(df["Status"].str.contains("Full working day should be 8 hrs", na=False)):
                    issues.append("Has non-standard hours")
                if any(df["Status"] == "Leave/Holiday should be 0 or empty"):
                    issues.append("Incorrectly logged leave/holiday")
                if any(df["Status"] == "Missing hours for a working day"):
                    issues.append("Missing hours entries")
                if any(df["Status"] == "Invalid Hours Format"):
                    issues.append("Invalid hour format")
                review_msg = ", ".join(issues)
            else:
                review_msg = "OK"

            new_entries.append({
                "S.No": sno,
                "File Name": file_name,
                "Description": sheet_name,
                "Hours": total_hours,
                "Review": review_msg,
                "Validation Date": timestamp
            })
            sno += 1

        new_entry_df = pd.DataFrame(new_entries)

        summary_tracking = pd.concat([summary_tracking, new_entry_df], ignore_index=True)

        summary_tracking.to_excel(summary_path, index=False)

    def add_to_master_summary(self, validation_result):
        """Add validation results to the master summary tracking file in the base validation directory."""
        master_summary_path = os.path.join(self.base_validation_dir, "master_validation_summary.xlsx")

        file_name = os.path.basename(validation_result["file_path"])
        validation_folder = os.path.basename(self.current_validation_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(master_summary_path):
            try:
                master_summary = pd.read_excel(master_summary_path)
            except:
                master_summary = pd.DataFrame(columns=["S.No", "File Name", "Description", "Hours", "Review",
                                                     "Validation Folder", "Validation Date"])
        else:
            master_summary = pd.DataFrame(columns=["S.No", "File Name", "Description", "Hours", "Review",
                                                 "Validation Folder", "Validation Date"])

        new_entries = []
        start_sno = 1
        if not master_summary.empty and "S.No" in master_summary.columns:
            try:
                start_sno = master_summary["S.No"].max() + 1
            except:
                start_sno = 1

        sno = start_sno
        for sheet_name, df in validation_result["validated_sheets"].items():
            total_hours = 0
            if "Hours" in df.columns:
                total_hours = df["Hours"].sum()

            review_msg = ""
            if any(df["Status"] != "Valid"):
                issues = []
                if any(df["Status"] == "Half-day detected"):
                    issues.append("Contains half-days")
                if any(df["Status"].str.contains("Full working day should be 8 hrs", na=False)):
                    issues.append("Has non-standard hours")
                if any(df["Status"] == "Leave/Holiday should be 0 or empty"):
                    issues.append("Incorrectly logged leave/holiday")
                if any(df["Status"] == "Missing hours for a working day"):
                    issues.append("Missing hours entries")
                if any(df["Status"] == "Invalid Hours Format"):
                    issues.append("Invalid hour format")
                review_msg = ", ".join(issues)
            else:
                review_msg = "OK"

            new_entries.append({
                "S.No": sno,
                "File Name": file_name,
                "Description": sheet_name,
                "Hours": total_hours,
                "Review": review_msg,
                "Validation Folder": validation_folder,
                "Validation Date": timestamp
            })
            sno += 1

        new_entry_df = pd.DataFrame(new_entries)

        master_summary = pd.concat([master_summary, new_entry_df], ignore_index=True)

        master_summary.to_excel(master_summary_path, index=False)

    def create_zip_archive(self, file_path, zip_path=None):
      """Create a ZIP archive containing the validated file and its summary."""
      if not os.path.exists(file_path):
        return None

      summary_path = os.path.join(os.path.dirname(file_path), "validation_summary.xlsx")
      if not os.path.exists(summary_path):

        if zip_path is None:
            file_name = os.path.basename(file_path)
            zip_name = f"{os.path.splitext(file_name)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(self.output_dir, zip_name)

      try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(file_path, os.path.basename(file_path), zipfile.ZIP_DEFLATED)
            if os.path.exists(summary_path):
                zipf.write(summary_path, os.path.basename(summary_path), zipfile.ZIP_DEFLATED)

        return zip_path
      except Exception as e:
        return None


    def create_new_version(self, file_path):
        """Create a new version of the sheet and archive the old one."""
        if not os.path.exists(file_path):
            return None, None

        file_name = os.path.basename(file_path)
        file_base = os.path.splitext(file_name)[0]
        file_ext = os.path.splitext(file_name)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{file_base}_v{timestamp}{file_ext}"
        archive_path = os.path.join(self.archive_dir, archive_name)

        try:
            shutil.copy2(file_path, archive_path)
            return file_path, archive_path
        except Exception as e:
            return None, None

    def generate_monthly_template(self, month=None, year=None):
        """Generate a new template for a specific month."""
        current_date = datetime.now()
        if month is None:
            if current_date.month == 12:
                month = 1
                year = current_date.year + 1
            else:
                month = current_date.month + 1
                year = current_date.year
        elif year is None:
            year = current_date.year

        month_name = calendar.month_name[month]
        _, num_days = calendar.monthrange(year, month)
        data = []
        for day in range(1, num_days + 1):
            date = datetime(year, month, day)
            weekday = date.strftime("%A")

            if weekday in ["Saturday", "Sunday"]:
                client = "Weekend"
                hours = 0
            else:
                client = ""  
                hours = 8    

            data.append({
                "Date": date,
                "Day": weekday,
                "Project": client,
                "Description": "",  
                "Hours": hours
            })
        monthly_df = pd.DataFrame(data)
        output_name = f"Timesheet_{month_name}_{year}.xlsx"
        output_path = os.path.join(self.output_dir, output_name)

        try:
            monthly_df.to_excel(output_path, index=False, sheet_name=f"{month_name} {year}")
            return output_path
        except Exception as e:
            return None

def main():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    media_dir = os.path.join(base_dir, 'media')
    output_dir = os.path.join(media_dir, 'timesheet_outputs')
    archive_dir = os.path.join(media_dir, 'timesheet_archives')
    validation_dir = os.path.join(media_dir, 'timesheet_validations')
    
    for directory in [output_dir, archive_dir, validation_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    validator = TimeValidator()
    output_manager = OutputManager(output_dir, archive_dir, validation_dir)
    return validator, output_manager

if __name__ == "__main__":
    main()