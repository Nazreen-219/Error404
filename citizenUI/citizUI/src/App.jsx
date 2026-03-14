import { useEffect, useMemo, useState } from 'react'
import chattisgarhLogo from '../chattisgarhLogo.png'
import './App.css'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts"
const translations = {
  hi: {
    dashboard: "CSC ऑपरेटर डैशबोर्ड",
    subtitle: "नागरिक सेवाओं के लिए AI सहायक प्रणाली",
    notifications: "सूचनाएँ",
    logout: "लॉगआउट",
    operator: "ऑपरेटर",
    applications: "आवेदन सूची",
    search: "आवेदन खोजें..."
  },
  en: {
    dashboard: "CSC Operator Dashboard",
    subtitle: "AI Assistant for Citizen Services",
    notifications: "Notifications",
    logout: "Logout",
    operator: "Operator",
    applications: "Application Queue",
    search: "Search applications..."
  }
}
function App() {
  const [analyticsData, setAnalyticsData] = useState([
    { name: "Mon", applications: 12, completed: 8 },
    { name: "Tue", applications: 19, completed: 11 },
    { name: "Wed", applications: 8, completed: 6 },
    { name: "Thu", applications: 15, completed: 10 },
    { name: "Fri", applications: 22, completed: 18 },
  ])
  const [liveStats, setLiveStats] = useState({
    activeKiosk: 128,
    applicationsToday: 248,
    processedToday: 196,
    pending: 52,
  })
  const alerts = [
  "आवेदन #A-1092 में आधार दस्तावेज़ नहीं मिला",
  "PMAY आवेदन #P-771 में अस्वीकृति की संभावना",
  "पेंशन योजना के लिए पात्रता मेल नहीं खा रही",
]
  const [lang,setLang] = useState("hi")
  const t = translations[lang]
  const liveUsagePercent = useMemo(() => {
    const { processedToday, applicationsToday } = liveStats
    if (applicationsToday === 0) return 0
    return Math.round((processedToday / applicationsToday) * 100)
  }, [liveStats])

  useEffect(() => {
    const initGoogleTranslate = () => {
      if (!window.google || !window.google.translate) return
      const container = document.getElementById('google_translate_element')
      if (!container) return
      container.innerHTML = ''
      new window.google.translate.TranslateElement(
        { pageLanguage: 'hi', autoDisplay: false },
        'google_translate_element'
      )
    }

    window.googleTranslateElementInit = initGoogleTranslate

    const existing = document.getElementById('google-translate-script')
    if (!existing) {
      const script = document.createElement('script')
      script.id = 'google-translate-script'
      script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'
      script.async = true
      document.body.appendChild(script)
    } else {
      initGoogleTranslate()
    }

    const interval = setInterval(() => {
      setLiveStats((prev) => {
        const applicationsToday = prev.applicationsToday + Math.floor(Math.random() * 4)
        const processedToday = prev.processedToday + Math.floor(Math.random() * 3)
        const pending = Math.max(0, applicationsToday - processedToday)
        const activeKiosk = prev.activeKiosk + (Math.random() > 0.7 ? 1 : 0) - (Math.random() > 0.85 ? 1 : 0)
        return {
          activeKiosk: Math.max(90, activeKiosk),
          applicationsToday,
          processedToday: Math.min(applicationsToday, processedToday),
          pending,
        }
      })

      setAnalyticsData((prev) => {
        const next = prev.slice(1)
        const last = prev[prev.length - 1]
        const applications = Math.max(6, last.applications + (Math.random() > 0.5 ? 2 : -1))
        const completed = Math.max(4, Math.min(applications, last.completed + (Math.random() > 0.6 ? 2 : -1)))
        const label = `T${Date.now() % 1000}`
        return [...next, { name: label, applications, completed }]
      })
    }, 2000)

    return () => {
      clearInterval(interval)
      if (window.googleTranslateElementInit) {
        delete window.googleTranslateElementInit
      }
    }
  }, [])
  const summaryCards = [
    { label: 'आज प्राप्त आवेदन', value: '25', tone: 'bg-orange-100 text-orange-900' },
    { label: 'लंबित आवेदन', value: '10', tone: 'bg-yellow-100 text-yellow-900' },
    { label: 'अस्वीकृत दस्तावेज़', value: '3', tone: 'bg-red-100 text-red-900' },
    { label: 'AI सुझाव', value: '14', tone: 'bg-green-100 text-green-900' },
  ]

  const queueRows = [
    { name: 'रमेश कुमार', service: 'आय प्रमाण पत्र', status: 'लंबित', risk: 'कम' },
    { name: 'सीता देवी', service: 'प्रधानमंत्री आवास योजना', status: 'प्रक्रिया में', risk: 'मध्यम' },
    { name: 'अमान अली', service: 'जन्म प्रमाण पत्र', status: 'लंबित', risk: 'कम' },
    { name: 'काव्या सिंह', service: 'आयुष्मान भारत', status: 'समीक्षा', risk: 'अधिक' },
  ]

  function translatePage(lang) {
    setLang(lang)
    const select = document.querySelector(".goog-te-combo")
    if (!select) return
    select.value = lang
    select.dispatchEvent(new Event("change"))
  }

  return (
    <div className="min-h-screen bg-[#F5F6F8] text-gray-800">

      {/* HEADER */}
      <header className="bg-[#FF9933] text-black">
        <div className="flex justify-between items-center px-6 py-4">

          <div className="flex items-center gap-3 ">
            <div className="flex items-center justify-center bg-white p-1 rounded-full">
            <img
              src={chattisgarhLogo}
              alt="Chhattisgarh Logo"
              className="h-15 w-12 object-contain"
            />
</div>

            <div>
              <div className="font-semibold text-lg">{t.dashboard}</div>
              <div className="text-xs">{t.subtitle}</div>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm">
          {t.notifications}

          {/* hidden translator container */}
          <div id="google_translate_element" className="hidden"></div>
             <div className="flex items-center gap-4 text-sm">

            <button
            onClick={()=>translatePage("hi")}
            className="border border-black px-2 py-1"
            >
            हिन्दी
            </button>

            <button
            onClick={()=>translatePage("en")}
            className="border border-black px-2 py-1"
            >
            English
            </button>

            <span>ऑपरेटर: राहुल</span>

            <button className="bg-black text-white px-4 py-1">
            लॉगआउट
            </button>

</div>

            
          </div>

        </div>
      </header>

      <div className="grid grid-cols-12">

        {/* SIDEBAR */}
        <aside className="col-span-2 bg-white border-r">

          <div className="p-4 font-semibold text-sm border-b">
            ऑपरेटर मेनू
          </div>

          <ul className="text-sm">

            {[
              t.dashboard,
              'नया आवेदन',
              'आवेदन सूची',
              'दस्तावेज़ सत्यापन',
              'योजना पात्रता',
              'AI सहायक',
              'रिपोर्ट',
              'सेटिंग्स',
            ].map((item, i) => (

              <li
                key={item}
                className={`px-4 py-3 border-b cursor-pointer hover:bg-orange-50 ${
                  i === 0 ? 'bg-orange-100 font-semibold border-l-4 border-[#FF9933]' : ''
                }`}
              >
                {item}
              </li>

            ))}

          </ul>

        </aside>

        {/* MAIN */}
        <main className="col-span-10 p-6 space-y-6">

          {/* SUMMARY CARDS */}
          <section className="grid grid-cols-4 gap-4">

            {summaryCards.map((card) => (
              <div key={card.label} className={`border p-4 ${card.tone}`}>
                <div className="text-sm">{card.label}</div>
                <div className="text-2xl font-bold mt-2">{card.value}</div>
              </div>
            ))}

          </section>
         
         {/* analytics section */}
          {/* ALERTS */}
          <section className="bg-white text-red-400 border p-4">

          <h3 className="font-semibold mb-3">
          सूचनाएँ
          </h3>

          <div className="ticker-wrapper">

          <div className="ticker text-white">

          {[...alerts, ...alerts].map((alert, index) => (

          <span key={index} className="ticker-item">

          ⚠ {alert}

          </span>

          ))}

          </div>

          </div>

          </section>

         {/* analytics Section */}
         <section className="bg-white border p-4">

        <h2 className="font-semibold mb-4">
        रियल टाइम सेवा विश्लेषण
        </h2>
        
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="border p-3 bg-orange-50">
            <div className="text-xs uppercase tracking-wide text-orange-700">सक्रिय CSC केंद्र</div>
            <div className="text-2xl font-bold text-orange-900">{liveStats.activeKiosk}</div>
          </div>
          <div className="border p-3 bg-blue-50">
            <div className="text-xs uppercase tracking-wide text-blue-700">आज प्राप्त आवेदन</div>
            <div className="text-2xl font-bold text-blue-900">{liveStats.applicationsToday}</div>
          </div>
          <div className="border p-3 bg-green-50">
            <div className="text-xs uppercase tracking-wide text-green-700">आज संसाधित आवेदन</div>
            <div className="text-2xl font-bold text-green-900">{liveStats.processedToday}</div>
          </div>
          <div className="border p-3 bg-gray-50">
            <div className="text-xs uppercase tracking-wide text-gray-600">सेवा उपयोग प्रतिशत</div>
            <div className="text-2xl font-bold text-gray-900">{liveUsagePercent}%</div>
          </div>
        </div>

        <div className="w-full h-64">

        <ResponsiveContainer width="100%" height="100%">

        <BarChart data={analyticsData}>

        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="name" />

        <YAxis />

        <Tooltip />

        <Bar dataKey="applications" fill="#FF9933" name="Applications" />

        <Bar dataKey="completed" fill="#16a34a" name="Completed" />

        </BarChart>

        </ResponsiveContainer>

        </div>

        </section>

          {/* APPLICATION TABLE */}
          <section className="bg-white border">

            <div className="flex justify-between items-center p-4 border-b">

              <h2 className="font-semibold">
                आवेदन सूची
              </h2>

              <input
                placeholder="आवेदन खोजें..."
                className="border px-3 py-1 text-sm focus:outline-none focus:border-[#FF9933]"
              />

            </div>

            <table className="w-full text-sm">

              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2 text-left">नागरिक</th>
                  <th className="p-2 text-left">सेवा</th>
                  <th className="p-2 text-center">स्थिति</th>
                  <th className="p-2 text-center">जोखिम</th>
                  <th className="p-2 text-center">कार्य</th>
                </tr>
              </thead>

              <tbody>

                {queueRows.map((row) => (

                  <tr key={row.name} className="border-t">

                    <td className="p-2">{row.name}</td>
                    <td className="p-2">{row.service}</td>
                    <td className="p-2 text-center">{row.status}</td>
                    <td className="p-2 text-center">{row.risk}</td>

                    <td className="p-2 flex justify-center gap-2">

                      <button className="bg-[#FF9933] text-black px-2 py-1 text-xs">
                        सत्यापित
                      </button>

                      <button className="bg-green-600 text-white px-2 py-1 text-xs">
                        स्वीकृत
                      </button>

                      <button className="bg-red-600 text-white px-2 py-1 text-xs">
                        अस्वीकार
                      </button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </section>

         
        </main>

      </div>
    </div>
  )
}

export default App

