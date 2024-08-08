//
//  SongsByTimestampView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 6/5/24.
//

import SwiftUI

let ADDITIONAL_SONG_COUNT = 20

struct ScrobblesByTimestampView: View {
    @State var globalData: GlobalData?
    @State var scrobbles: [Scrobble]
    @State var isLoading: Bool = false
    @AppStorage("remote_url") var url: URL = URL(string: DEFAULT_URL)!
    
    init(globalData: GlobalData? = nil) {
        self.globalData = globalData
        self.scrobbles = globalData?.ten_most_recent_scrobbles ?? []
    }
    
    func loadMoreSongs() async {
        isLoading = true
        
        guard let beginningDate = scrobbles.last?.played_at else { return }
        
        let remoteURLString = "/scrobbles_paginated?from=\(Int(beginningDate.timeIntervalSince1970))&count=\(ADDITIONAL_SONG_COUNT)"
        let remoteURL = URL(string: remoteURLString, relativeTo: url) ?? URL(string: DEFAULT_URL)!
        
        guard let (data, response) = try? await URLSessionManager.normalSessionManager.data(from: remoteURL) else { return }
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else { return }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        guard let new_songs = try? decoder.decode([Scrobble].self, from: data) else { return }
        
        isLoading = false
        
        self.scrobbles.append(contentsOf: new_songs)
    }
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(scrobbles, id: \.played_at) { song in
                    NavigationLink {
                        SongDetailView(song: Song(id: song.id))
                    } label: {
                        ScrobbleCell(name: song.name, played_at: song.played_at, image_url: song.cover_image_url)
                    }
                    .onAppear {
                        if self.scrobbles.last == song {
                            Task {
                                await self.loadMoreSongs()
                            }
                        }
                    }
                }
                .navigationTitle("All Scrobbles")
            }
            .animation(.snappy, value: scrobbles)
        }
    }
}
