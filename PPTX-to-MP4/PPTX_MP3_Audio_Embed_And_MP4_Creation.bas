Attribute VB_Name = "PPTX_Audio_Embedder"
Sub EmbedMP3AudioAndExportToMP4()
    Dim ppt As Presentation
    Dim slide As slide
    Dim shape As shape
    Dim audioPath As String
    Dim audioFile As String
    Dim duration As Double
    Dim i As Integer
    Dim fileDialog As fileDialog
    Dim outputVideoFile As String
    Dim missingFiles As String

    Set ppt = ActivePresentation

    ' Choose folder for MP3 files
    Set fileDialog = Application.FileDialog(msoFileDialogFolderPicker)
    fileDialog.Title = "Select folder containing MP3 audio files"

    If fileDialog.Show = -1 Then
        audioPath = fileDialog.SelectedItems(1) & "\"
    Else
        MsgBox "No folder selected. Exiting.", vbExclamation
        Exit Sub
    End If

    outputVideoFile = InputBox("Enter full path for the output video file (MP4)", "Output Video Path", "C:\path\to\output\final_video.mp4")
    If outputVideoFile = "" Then
        MsgBox "No output file path provided. Exiting.", vbExclamation
        Exit Sub
    End If

    ppt.SlideShowSettings.AdvanceMode = ppSlideShowUseSlideTimings
    missingFiles = ""

    For i = 1 To ppt.Slides.Count
        audioFile = audioPath & "slide_" & i & ".mp3"
        If Dir(audioFile) <> "" Then
            ' Add MP3 to slide
            Set shape = ppt.Slides(i).Shapes.AddMediaObject2(audioFile, _
                LinkToFile:=msoFalse, _
                SaveWithDocument:=msoTrue, _
                Left:=50, Top:=50)

            ' Position speaker icon (optional hide)
            With shape
                .LockAspectRatio = msoTrue
                .Width = 20
                .Top = ppt.PageSetup.SlideHeight - .Height - 10
                .Left = ppt.PageSetup.SlideWidth - .Width - 10
                .Visible = msoTrue ' Set to msoFalse to hide
            End With

            ' Auto-play settings (modern handling)
            shape.AnimationSettings.PlaySettings.PlayOnEntry = msoTrue
            shape.AnimationSettings.PlaySettings.LoopUntilStopped = msoFalse

            ' Use media duration for slide timing
            duration = shape.MediaFormat.Length / 1000 ' ms to seconds
            With ppt.Slides(i).SlideShowTransition
                .AdvanceOnTime = msoTrue
                .AdvanceTime = duration
            End With
        Else
            missingFiles = missingFiles & vbCrLf & "slide_" & i & ".mp3"
        End If
    Next i

    ' Final reporting
    If missingFiles <> "" Then
        MsgBox "The following audio files were missing:" & vbCrLf & missingFiles, vbExclamation
    End If

    ' Export to MP4
    ppt.CreateVideo FileName:=outputVideoFile, UseTimingsAndNarrations:=msoTrue
    MsgBox "MP4 export started. It may take a few minutes to complete.", vbInformation
End Sub
