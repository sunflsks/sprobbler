//
//  Top10View.swift
//  spotipie
//
//  Created by Sudhip Nashi on 27/07/24.
//

import SwiftUI

struct Top10ArtistView: View {
    @State var globalData: GlobalData?
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(globalData?.ten_most_played_artists ?? [], id: \.id) { artist in
                    NavigationLink {
                        EmptyView()
                    } label: {
                        ArtistCell(name: artist.name, play_count: artist.play_count, id: artist.id)
                    }
                }
                .navigationTitle("Top 10 Artists")
            }
        }
    }
}
