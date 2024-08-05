//
//  GlobalDataView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import SwiftUI


struct ContentView: View {
    @State var globalData: GlobalData?
    
    @State var weeklyReport: Report?
    @State var monthlyReport: Report?
    @State var yearlyReport: Report?
    @State var allTimeReport: Report?
    
    @AppStorage("remote_url") var url: URL = URL(string: DEFAULT_URL)!
    
    func refreshData() async {
        globalData = try? await GlobalData.getGlobalData(base_url: url)
        
        weeklyReport = try? await Report.load(base_url: url, time: .week)
        monthlyReport = try? await Report.load(base_url: url, time: .month)
        yearlyReport = try? await Report.load(base_url: url, time: .year)
        allTimeReport = try? await Report.load(base_url: url, time: .allTime)

    }
    
    var body: some View {
        NavigationStack {
            List {
                Section(header: Text("Most Recent Scrobbles")) {
                    ForEach(globalData?.ten_most_recent_scrobbles ?? [], id: \.played_at) { song in
                        NavigationLink {
                            SongDetailView(song: Song(id: song.id))
                        } label: {
                            ScrobbleCell(name: song.name, played_at: song.played_at, image_url: song.cover_image_url)
                        }
                    }
                    
                    NavigationLink {
                        ScrobblesByTimestampView(globalData: globalData)
                    } label: {
                        HStack {
                            Image(systemName: "music.note.list")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Show More")
                        }
                    }
                }
                
                Section(header: Text("Reports" )) {
                    ForEach([weeklyReport, monthlyReport, yearlyReport, allTimeReport], id: \.?.id) { value in
                        if let report = value, let unwrappedTime = report.time {
                            let title = Report.times.label(time: unwrappedTime).trim()
                            
                                NavigationLink {
                                    ReportView(report: report, title: title)
                                } label: {
                                    HStack {
                                        Image(systemName: "list.dash")
                                            .resizable()
                                            .scaledToFit()
                                            .frame(width: 40, height: 40)
                                            .cornerRadius(5)
                                        
                                        Text(title)
                                    }
                                }
                            }
                        }
                }
                
                
                Section(header: Text("Settings")) {
                    NavigationLink {
                        SettingsView()
                    } label: {
                        HStack {
                            Image(systemName: "gear")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 40, height: 40)
                                .cornerRadius(5)
                            
                            Text("Settings")
                        }
                    }
                }
            }
            .animation(.snappy, value: UUID())
            .navigationTitle("Spotipie")
        }
        .task {
            await refreshData()
        }
        .refreshable {
            await refreshData()
        }
    }
}
