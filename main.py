from pytube import *
import os
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
from tkinter.messagebox import *
from threading import *
import re

file_size = 0
resolution = "1080p"

OPTIONS = [
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
    "Only Audio (mp3)"
]

def progress_function(stream=None, chunk=None, remaining=None):
    file_downloaded = (file_size-remaining)
    per = round((file_downloaded/file_size)*100, 1)
    print(str(per)+'%')
    progress['value'] = per
    main.update_idletasks()

def combine_audio(vidname, audname, outname):
    import moviepy.editor as mpe
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname)

# function start download to start the download of files
def startDownload():
    global file_size
    try:
        URL = urlField.get()
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        pat = re.compile(regex)
        if not re.fullmatch(pat, URL):
            showinfo("Enter valid URL", 'Enter a valid URL')
        else:
            dBtn.config(text='Please wait...')
            dBtn.config(state=DISABLED)
            path_save = askdirectory()
            if not path_save:
                dBtn.config(state=NORMAL)
                urlField.delete(0, END)
                label.pack_forget()
                desc.pack_forget()
                myCombo.current(0)
                progress['value'] = 0
                dBtn.config(text='Start Download')
                return
            ob = YouTube(URL, on_progress_callback=progress_function)
            print(ob.streams.filter(res=resolution).all())
            available_res = [stream.resolution for stream in ob.streams.filter(progressive=True).all()]
            available_res.append("Only Audio (mp3)")
            if(resolution not in available_res):
                showinfo("Download Cannot be completed", f'Video Resolution doesn\'t exists!\nAvailable resolutions are : {str(available_res)[1:-1]}')
                dBtn.config(state=NORMAL)
                urlField.delete(0, END)
                label.pack_forget()
                desc.pack_forget()
                myCombo.current(0)
                progress['value'] = 0
                dBtn.config(text='Start Download')
                return
            if resolution!="Only Audio (mp3)" and ob.streams.filter(res=resolution, progressive=True).first() == None:
                showinfo("Video Audio Download", 'Video and Audio will be downloaded Seperately and will be merged due to Youtube issues, so video download will take some time. Please wait Patiently.')
                extension = ".mp4"
                strm1 = ob.streams.filter(only_audio=True).first()
                strm2 = ob.streams.filter(res=resolution).first()
                x = ob.description.split("|")
                file_size = strm1.filesize + strm2.filesize
                dfile_size = file_size
                dfile_size /= 1000000
                dfile_size = round(dfile_size, 2)
                label.config(text='Size: ' + str(dfile_size) + ' MB')
                label.pack(side=TOP, pady=10)
                desc.config(text=re.sub(r'[^a-zA-Z0-9 ]', r'', ob.title) + '\n\n' + 'Channel Name: ' + ob.author + '\n\n' + 'Length: ' + str(round(ob.length/60, 1)) + ' mins\n\n' + 'Views: ' + str(ob.views), width=200, wraplength=450, justify=CENTER)
                desc.pack(side=TOP, fill=X, padx=10, pady=15)
                strm1.download(path_save, "youtube_audio.mp3")
                strm2.download(path_save, "youtube_video.mp4")
                path1 = os.path.join(path_save, "youtube_audio.mp3").replace("\\","/")
                path2 = os.path.join(path_save, "youtube_video.mp4").replace("\\","/")
                out_path = os.path.join(path_save, re.sub(' +', ' ', re.sub(r'[^a-zA-Z0-9 ]', r'', strm1.title))+extension).replace("\\","/")
                progress.config(mode="indeterminate")
                progress.start()
                combine_audio(path2, path1, out_path)
                os.remove(path1)
                os.remove(path2)
                progress.stop()
                progress.config(mode="determinate")
                showinfo("Download Finished", 'Downloaded Successfully')
            else:
                if resolution == "Only Audio (mp3)":
                    strm = ob.streams.filter(only_audio=True).first()
                    extension = ".mp3"
                else:
                    strm = ob.streams.filter(res=resolution, progressive=True).first()
                    extension = ".mp4"
                x = ob.description.split("|")
                file_size = strm.filesize
                dfile_size = file_size
                dfile_size /= 1000000
                dfile_size = round(dfile_size, 2)
                label.config(text='Size: ' + str(dfile_size) + ' MB')
                label.pack(side=TOP, pady=10)
                desc.config(text=re.sub(r'[^a-zA-Z0-9 ]', r'', ob.title) + '\n\n' + 'Channel Name: ' + ob.author + '\n\n' + 'Length: ' + str(round(ob.length/60, 1)) + ' mins\n\n' + 'Views: ' + str(ob.views), width=200, wraplength=450, justify=CENTER)
                desc.pack(side=TOP, fill=X, padx=10, pady=15)
                strm.download(path_save, re.sub(r'[^a-zA-Z0-9 ]', r'', strm.title)+extension)
                showinfo("Download Finished", 'Downloaded Successfully')
            dBtn.config(state=NORMAL)
            urlField.delete(0, END)
            label.pack_forget()
            desc.pack_forget()
            myCombo.current(0)
            progress['value'] = 0
            dBtn.config(text='Start Download')

    except Exception as e:
        print(e)
        print('Error!!')
        showinfo("ERROR", 'OOPS! AN ERROR OCCURED')
        dBtn.config(state=NORMAL)
        urlField.delete(0, END)
        label.pack_forget()
        desc.pack_forget()
        myCombo.current(0)
        progress['value'] = 0
        dBtn.config(text='Start Download')


def startDownloadthread():
    thread = Thread(target=startDownload)
    thread.start()

def click(event):
    URL = urlField.get()
    if(URL == "Enter Video URL"):
        urlField.config(state=NORMAL)
        urlField.delete(0, END)

def leave(event):
    URL = urlField.get()
    if(not URL):
        urlField.insert(0, "Enter Video URL")
        urlField.config(state=DISABLED)

def comboClick(event):
    global resolution
    resolution=myCombo.get()
    print(resolution)

main = Tk()

progress = ttk.Progressbar(main, orient = HORIZONTAL, length = 400, mode = 'determinate')

main.title("YouTube Downloader")
main.config(bg='#3498DB')

main.iconbitmap('youtube-ios-app.ico')

main.geometry("500x600")

file = PhotoImage(file='photo.png')
headingIcon = Label(main, image=file)
headingIcon.pack(side=TOP, pady=10)

urlField = Entry(main, font=("Times New Roman", 18), justify=CENTER)
urlField.insert(0, "Enter Video URL")
urlField.config(state=DISABLED)
urlField.bind("<Button-1>", click)
urlField.bind("<Leave>", leave)
urlField.pack(side=TOP, fill=X, padx=10, pady=15)

myCombo = ttk.Combobox(main, state="readonly", width = 27, value=OPTIONS)
myCombo.current(0)
myCombo.bind("<<ComboboxSelected>>", comboClick)
myCombo.pack()

progress.pack(padx=10, pady=15)

dBtn = Button(main, text="Start Download", font=("Times New Roman", 18), relief='ridge', activeforeground='red', command=startDownloadthread)
dBtn.pack(side=TOP)
label = Label(main, text='')
desc = Label(main, text='')
main.mainloop()