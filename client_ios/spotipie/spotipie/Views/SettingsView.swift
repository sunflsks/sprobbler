//
//  SettingsView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 02/08/24.
//

import SwiftUI

struct SettingsView: View {
    @AppStorage("remote_url") var url: URL = URL(string: DEFAULT_URL)!
    
    var body: some View {
        Form {
            Section("Server Address") {
                TextField("https://test.com:8080", text: Binding(get: {
                    url.absoluteString
                }, set: {
                    url = URL(string: $0) ?? URL(string: DEFAULT_URL)!
                }))
                .keyboardType(.URL)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
            }
        }
        .navigationTitle("Settings")
    }
}
