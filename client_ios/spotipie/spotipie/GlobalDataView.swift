//
//  GlobalDataView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import SwiftUI


struct GlobalDataView: View {
    @State var globalData: GlobalData?
    
    func refreshData() async {
        globalData = try? await getGlobalData()
    }
    
    func dateFromISO(str: String) -> Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFractionalSeconds, .withInternetDateTime]
        return formatter.date(from: str)
    }
    
    var body: some View {
        Text("Recent Scrobbles").font(.title)
        
        List(globalData?.ten_most_recent_scrobbles ?? [], id: \.played_at) { song in
            ScrobbleCellView(name: song.name, played_at: dateFromISO(str: song.played_at), image_url: song.cover_image_url)
        }
        .task {
            await refreshData()
        }
        .refreshable {
            await refreshData()
        }
    }
}
