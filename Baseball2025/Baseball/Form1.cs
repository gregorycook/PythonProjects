using System;
using System.Configuration;
using System.Data;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

using CefSharp;
using CefSharp.Handler;

namespace Baseball
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            chromiumWebBrowser1.RequestHandler = new CustomRequestHandler();

            Task.Run(() => SuckStats());
        }

        private object sourceLockObject = new object();
        private string source;

        private void AddStringToBox(string stuff)
        {
            textBox1.Invoke(new Action(() => { textBox1.Text = textBox1.Text + stuff; }));
        }

        private void SuckStats()
        {
            string scriptDirectory = ConfigurationManager.AppSettings["ScriptPath"];
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/standings", Path.Combine(scriptDirectory, "standings.txt"));
            AddStringToBox("Done downloading standings json\r\n");
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/team/schedule/_/name/sea/seasontype/2/half/1", Path.Combine(scriptDirectory, "schedule.txt"));
            // LoadPageAndSave("https://www.espn.com/mlb/team/schedule/_/name/sea/seasontype/2/half/2", Path.Combine(scriptDirectory, "schedule.txt"));
            AddStringToBox("Done downloading schedule json\r\n");
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/team/stats/_/name/sea", Path.Combine(scriptDirectory, "hitting.txt"));
            AddStringToBox("Done downloading hitting json\r\n");
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/team/stats/_/type/pitching/name/sea", Path.Combine(scriptDirectory, "pitching.txt"));
            AddStringToBox("Done downloading pitching json\r\n");
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/team/splits/_/name/sea", Path.Combine(scriptDirectory, "splits.txt"));
            AddStringToBox("Done downloading splits json\r\n");
            Thread.Sleep(1000);

            LoadPageAndSave("https://www.espn.com/mlb/team/stats/_/type/fielding/name/sea", Path.Combine(scriptDirectory, "fielding.txt"));
            AddStringToBox("Done downloading fielding json\r\n");

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "python";
            start.Arguments = " publish_stats.py";
            start.WorkingDirectory = scriptDirectory;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    while (!reader.EndOfStream)
                    {
                        string result = reader.ReadToEnd();
                        AddStringToBox(result);
                    }
                }
            }

            System.Windows.Forms.Application.Exit();
        }

        private void LoadPageAndSave(string url, string outputFile)
        {
            source = String.Empty;
            Thread t = new Thread(() => GetPageSource(url));
            t.Start();
            t.Join();

            byte[] bytes = Encoding.UTF8.GetBytes(source);
            source = Encoding.ASCII.GetString(bytes.Where(c => c != 0x9d).ToArray());
            File.Delete(outputFile);
            File.WriteAllText(outputFile, source);
        }


        private void GetPageSource(string url)
        {
            bool done = false;
            chromiumWebBrowser1.LoadUrl(url);
            while (!done)
            {
                Thread.Sleep(1000);
                lock (sourceLockObject)
                {
                    if (!String.IsNullOrEmpty(source))
                    {
                        done = true;
                    }
                }
            }
        }

        
        private void chromiumWebBrowser1_FrameLoadEnd(object sender, CefSharp.FrameLoadEndEventArgs e)
        {
            if (e.Frame.IsMain)
            {
                e.Frame.GetSourceAsync().ContinueWith(taskHtml =>
                {
                    lock (sourceLockObject)
                    {
                        source = taskHtml.Result;
                    }
                });
            }
        }

        public class CustomResourceRequestHandler : ResourceRequestHandler
        {
            protected override CefReturnValue OnBeforeResourceLoad(IWebBrowser chromiumWebBrowser, IBrowser browser, IFrame frame, IRequest request, IRequestCallback callback)
            {
                var headers = request.Headers;
                // headers["User-Agent"] = "My User Agent";
                // request.Headers = headers;
                foreach(var x in headers.AllKeys) {

                    Console.WriteLine($"{x}: {headers[x]}");
 
                }
                return CefReturnValue.Continue;
            }
        }

        public class CustomRequestHandler : RequestHandler
        {
            protected override IResourceRequestHandler GetResourceRequestHandler(IWebBrowser chromiumWebBrowser, IBrowser browser, IFrame frame, IRequest request, bool isNavigation, bool isDownload, string requestInitiator, ref bool disableDefaultHandling)
            {
                return new CustomResourceRequestHandler();
            }
        }

    }
}
