import os
import matplotlib.pyplot as plt
import pandas as pd

file_name = "patients.csv"


def check_file():
  """Initializes the CSV file with required columns if it doesn't exist."""
  if not os.path.exists(file_name):
    df = pd.DataFrame(columns=[
        "id",
        "name",
        "ward",
        "bed",
        "age",
        "gender",
        "disease",
        "payment",
        "date",
        "doctor",
    ])
    df.to_csv(file_name, index=False)


def admit():
  """Choice 1: Admit a new patient and save to CSV."""
  check_file()
  print("\n--- Admit Patient ---")
  pid = input("Enter patient ID: ").strip()

  # Check if ID already exists
  df = pd.read_csv(file_name)
  if not df.empty and pid in df["id"].astype(str).values:
    print(f"\nError: Patient with ID '{pid}' already exists!")
    return

  name = input("Enter patient name: ").strip()
  ward = input("Enter ward/room: ").strip()
  bed = input("Enter bed number: ").strip()
  try:
    age = int(input("Enter age: ").strip())
  except ValueError:
    print("\nInvalid age entered. Please enter a valid number.")
    return

  gender = input("Enter gender (Men/Women/Other): ").strip().lower()
  disease = input("Enter disease: ").strip()
  payment = (
      input("Enter payment status (complete/pending): ").strip().lower()
  )
  if payment not in ["complete", "pending"]:
    payment = "pending"  # Default fallback

  date = input("Enter admission date (YYYY-MM-DD): ").strip()
  doctor = input("Enter doctor allocated: ").strip()

  new_row = {
      "id": pid,
      "name": name,
      "ward": ward,
      "bed": bed,
      "age": age,
      "gender": gender,
      "disease": disease,
      "payment": payment,
      "date": date,
      "doctor": doctor,
  }

  df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
  df.to_csv(file_name, index=False)
  print("\nPatient admitted successfully!")


def display():
  """Choice 2: Display the 4-part graphical dashboard and summary data."""
  if not os.path.exists(file_name):
    print("\nNo records found. Please admit a patient first.")
    return

  df = pd.read_csv(file_name)
  if df.empty:
    print("\nNo data available. Please admit a patient first.")
    return

  print(f"\nTotal patients in record: {len(df)}")
  print("Opening graphical dashboard...")

  fig, axs = plt.subplots(2, 2, figsize=(14, 9))
  fig.suptitle(
      "Patient Admission Analysis Dashboard", fontsize=16, fontweight="bold"
  )

  # --- Top-Left: Bar graph for diseases (cleaned to group typos) ---
  df["disease_clean"] = df["disease"].str.lower().str.strip()
  dis_counts = df["disease_clean"].value_counts()

  axs[0, 0].bar(
      dis_counts.index, dis_counts.values, color="skyblue", edgecolor="black"
  )
  axs[0, 0].set_title("Patients by Disease", fontweight="bold")
  axs[0, 0].set_ylabel("Number of Patients")
  axs[0, 0].tick_params(axis="x", rotation=30)
  axs[0, 0].grid(axis="y", linestyle="--", alpha=0.5)

  # --- Top-Right: Pie chart for gender ---
  gen_counts = df["gender"].value_counts()
  if not gen_counts.empty:
    axs[0, 1].pie(
        gen_counts.values,
        labels=gen_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#ff9999", "#66b3ff", "#99ff99"],
    )
    axs[0, 1].set_title("Gender Distribution", fontweight="bold")

  # --- Bottom-Left: Line chart over Admission Dates (Adults vs Children) ---
  df["criteria"] = df["age"].apply(lambda x: "Child" if x < 18 else "Adult")

  # Group by date and criteria to count daily admissions
  date_trend = (
      df.groupby(["date", "criteria"])
      .size()
      .unstack(fill_value=0)
      .reset_index()
  )

  if "Adult" not in date_trend.columns:
    date_trend["Adult"] = 0
  if "Child" not in date_trend.columns:
    date_trend["Child"] = 0

  # Sort chronologically by date
  date_trend = date_trend.sort_values("date")

  # Plot Adult line (Red) and Child line (Blue) across dates on X-axis
  axs[1, 0].plot(
      date_trend["date"],
      date_trend["Adult"],
      marker="o",
      color="red",
      linewidth=2.5,
      label="Adults",
  )
  axs[1, 0].plot(
      date_trend["date"],
      date_trend["Child"],
      marker="o",
      color="blue",
      linewidth=2.5,
      label="Children",
  )

  axs[1, 0].set_title(
      "Daily Admissions Trend (Adults vs Children)", fontweight="bold"
  )
  axs[1, 0].set_xlabel("Admission Date")
  axs[1, 0].set_ylabel("Patient Count")
  axs[1, 0].tick_params(axis="x", rotation=30)
  axs[1, 0].grid(True, linestyle="--", alpha=0.6)
  axs[1, 0].legend()

  # --- Bottom-Right: Text summary box ---
  total_patients = len(df)
  payment_complete = len(
      df[df["payment"].str.lower().str.strip() == "complete"]
  )
  payment_pending = len(df[df["payment"].str.lower().str.strip() == "pending"])

  axs[1, 1].axis("off")
  summary = (
      f"Total_patients: {total_patients}\n"
      f"Payment_complete: {payment_complete}\n"
      f"Payment_pending: {payment_pending}"
  )
  axs[1, 1].text(
      0.15,
      0.5,
      summary,
      fontsize=14,
      verticalalignment="center",
      bbox=dict(
          boxstyle="round,pad=1", facecolor="lightyellow", edgecolor="orange"
      ),
  )
  axs[1, 1].set_title("Summary Data", fontweight="bold")

  plt.tight_layout()
  plt.show()


def update():
  """Choice 3: Update patient payment status using their Patient ID."""
  if not os.path.exists(file_name):
    print("\nNo records found.")
    return

  df = pd.read_csv(file_name)
  if df.empty:
    print("\nNo records found.")
    return

  print("\n--- Update Patient Payment Status ---")
  pid = input("Enter patient ID to update: ").strip()

  match_mask = df["id"].astype(str) == pid
  if match_mask.any():
    current_status = df.loc[match_mask, "payment"].values[0]
    print(f"Current payment status for ID {pid}: {current_status}")

    new_status = (
        input("Enter new payment status (complete/pending): ").strip().lower()
    )
    if new_status not in ["complete", "pending"]:
      print("\nInvalid status! Please enter either 'complete' or 'pending'.")
      return

    df.loc[match_mask, "payment"] = new_status
    df.to_csv(file_name, index=False)
    print("\nPayment status updated successfully!")
  else:
    print("\nPatient ID not found.")


def delete_patient():
  """Choice 4: Delete a patient record from the CSV using Patient ID."""
  if not os.path.exists(file_name):
    print("\nNo records found.")
    return

  df = pd.read_csv(file_name)
  if df.empty:
    print("\nNo records found to delete.")
    return

  print("\n--- Delete Patient Record ---")
  pid = input("Enter patient ID to delete: ").strip()

  match_mask = df["id"].astype(str) == pid
  if match_mask.any():
    df = df[~match_mask]
    df.to_csv(file_name, index=False)
    print(f"\nSuccess: Patient with ID '{pid}' has been deleted from records.")
  else:
    print("\nPatient ID not found.")


def main():
  check_file()
  while True:
    print("\n==============================")
    print("  PATIENT ADMISSION SYSTEM   ")
    print("==============================")
    print("1. Admit a patient")
    print("2. Display overall admission data")
    print("3. Patient updation")
    print("4. Delete patient record")
    print("5. Exit")

    ch = input("Enter your choice: ").strip()

    if ch == "1":
      admit()
    elif ch == "2":
      display()
    elif ch == "3":
      update()
    elif ch == "4":
      delete_patient()
    elif ch == "5":
      print("\nExiting program. Goodbye!")
      break
    else:
      print("\nInvalid choice, try again.")


if __name__ == "__main__":
  main()