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
    
    var body: some View {
        List(globalData?.ten_most_recent_scrobbles ?? [], id: \.name) { song in
            Text(song.name)
        }
        .refreshable {
            await refreshData()
        }
    }
}

#Preview {
    GlobalDataView()
}
