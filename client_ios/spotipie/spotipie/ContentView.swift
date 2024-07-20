//
//  GlobalDataView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import SwiftUI


struct ContentView: View {
    @State var globalData: GlobalData?
    
    func refreshData() async {
        globalData = try? await GlobalData.getGlobalData()
    }
    
    var body: some View {
        NavigationStack {
            List(globalData?.ten_most_recent_scrobbles ?? [], id: \.played_at) { song in
                NavigationLink {
                    SongDetail(song: Song(id: song.track_id))
                } label: {
                    ScrobbleCell(name: song.name, played_at: dateFromISO(str: song.played_at), image_url: song.cover_image_url)
                }
            }
            NavigationLink {
                SongsByTimestampView(globalData: globalData)
            } label: {
                Text("Show More")
            }
            .navigationTitle("Recent Scrobbles")
        }
        .task {
            await refreshData()
        }
        .refreshable {
            await refreshData()
        }
    }
}
