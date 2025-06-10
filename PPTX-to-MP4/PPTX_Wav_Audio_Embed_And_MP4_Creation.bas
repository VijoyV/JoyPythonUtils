Attribute VB_Name = "PPTX_Audio_Embedder"
Sub EmbedAudioAndExportToMP4()
    Dim ppt As Presentation
    Dim slide As slide
    Dim shape As shape
    Dim audioPath As String
    Dim audioFile As String
    Dim duration As Double
    Dim i As Integer
    Dim fileDialog As fileDialog
    Dim outputVideoFile As String
    
    ' Get the active presentation
    Set ppt = ActivePresentation
    
    ' Open File Dialog to Select Audio Folder
    Set fileDialog = Application.fileDialog(msoFileDialogFolderPicker)
    fileDialog.Title = "Select the folder containing WAV audio files"
    
    If fileDialog.Show = -1 Then
        audioPath = fileDialog.SelectedItems(1) & "\"
    Else
        MsgBox "No folder selected. Exiting.", vbExclamation
        Exit Sub
    End If

    ' Ask for Output Video File Path
    outputVideoFile = InputBox("Enter full path for the output video file (MP4)", "Output Video Path", "C:\path\to\output\final_video.mp4")
    If outputVideoFile = "" Then
        MsgBox "No output file path provided. Exiting.", vbExclamation
        Exit Sub
    End If
    
    ' Set slide timings automatically
    ppt.SlideShowSettings.AdvanceMode = ppSlideShowUseSlideTimings
    
    ' Iterate through slides and embed audio
    For i = 1 To ppt.Slides.Count
        audioFile = audioPath & "slide_" & i & ".wav"
        If Dir(audioFile) <> "" Then
            ' Add audio to slide
            Set shape = ppt.Slides(i).Shapes.AddMediaObject2(audioFile, msoFalse, msoTrue, 50, 50)
            
            ' Hide the speaker icon or move it to the bottom-right
            With shape
                .LockAspectRatio = msoTrue
                .Width = 20  ' Make it smaller
                .Top = ppt.PageSetup.SlideHeight - .Height - 10  ' Move to bottom-right
                .Left = ppt.PageSetup.SlideWidth - .Width - 10
                .Visible = msoTrue  ' Change to `msoFalse` to hide it completely
            End With

            ' Ensure audio plays automatically
            With shape.AnimationSettings.PlaySettings
                .PlayOnEntry = msoTrue
                .LoopUntilStopped = msoFalse
            End With

            ' Get audio duration
            duration = shape.MediaFormat.Length / 1000
            ppt.Slides(i).SlideShowTransition.AdvanceOnTime = msoTrue
            ppt.Slides(i).SlideShowTransition.AdvanceTime = duration
        Else
            Debug.Print "Audio file missing: " & audioFile
        End If
    Next i

    ' Export the PPTX to MP4
    ppt.CreateVideo FileName:=outputVideoFile, UseTimingsAndNarrations:=msoTrue
    
    MsgBox "MP4 export started. This may take a few minutes.", vbInformation
End Sub

