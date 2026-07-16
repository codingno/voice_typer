import plistlib
import subprocess
import os

shortcut_data = {
    "WFWorkflowActions": [
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.dictatetext",
            "WFWorkflowActionParameters": {
                "WFDictateTextLanguage": "id-ID",
                "WFDictateTextStopListening": "After Short Pause"
            }
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.runapplescript",
            "WFWorkflowActionParameters": {
                "Script": """on run {input, parameters}
    set theText to input as string
    if theText is not "" then
        try
            set oldClipboard to the clipboard
        on error
            set oldClipboard to ""
        end try
        
        set the clipboard to theText
        delay 0.15
        
        tell application "System Events"
            keystroke "v" using {command down}
            delay 0.15
            key code 36 -- Enter (Return)
        end tell
        
        delay 0.5
        try
            set the clipboard to oldClipboard
        end try
    end if
    return input
end run"""
            }
        }
    ],
    "WFWorkflowClientVersion": "2600",
    "WFWorkflowIcon": {
        "WFWorkflowIconGlyphNumber": 59798,
        "WFWorkflowIconStartColor": 431817727
    },
    "WFWorkflowInputContentItemClasses": [
        "WFStringContentItem"
    ],
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowTypes": [
        "NCWidget",
        "QuickActions"
    ]
}

target_path = "/Users/codingno/Downloads/Dikte_dan_Enter.shortcut"

try:
    with open(target_path, "wb") as fp:
        plistlib.dump(shortcut_data, fp)
    print(f"Successfully generated shortcut at: {target_path}")
    
    # Try to open it using the open command to import it into the Shortcuts app
    print("Opening the shortcut to trigger macOS import prompt...")
    subprocess.run(["open", target_path])
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
