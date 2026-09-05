import os

import matches as m


sezone = [
    {'url': 'https://www.11v11.com/competitions/premier-league/2026/matches/', 'html_ime': 'sezona_2026.html'},
    {'url': 'https://www.11v11.com/competitions/premier-league/2025/matches/', 'html_ime': 'sezona_2025.html'},
]

strelci_url = [
    {'url': 'https://www.11v11.com/competitions/premier-league/2026/goal-scorers/', 'html_ime': 'strelci_2026.html'},
    {'url': 'https://www.11v11.com/competitions/premier-league/2025/goal-scorers/', 'html_ime': 'strelci_2025.html'},
]

directory = 'podatki'
csv_filename = 'tekme.csv'
strelci_csv_filename = 'strelci.csv'


def main():

    vse_tekme = []
    vsi_strelci = []

    for sezona in sezone:
        path_html_file = os.path.join(directory, sezona['html_ime'])

        if not os.path.exists(path_html_file):
            m.save_frontpage(sezona['url'], directory, sezona['html_ime'])

        tekme = m.from_file(directory, sezona['html_ime'], sezona)
        vse_tekme.extend(tekme)

    m.write_matches_to_csv(vse_tekme, directory, csv_filename)

    for sezona in strelci_url:
        path_html_file = os.path.join(directory, sezona['html_ime'])

        if not os.path.exists(path_html_file):
            m.save_frontpage(sezona['url'], directory, sezona['html_ime'])

        strelci = m.strelci_from_file(directory, sezona['html_ime'])
        vsi_strelci.extend(strelci)

    m.write_matches_to_csv(vsi_strelci, directory, strelci_csv_filename)

    print(f"Shranjenih {len(vse_tekme)} tekem in {len(vsi_strelci)} strelcev.")


if __name__ == '__main__':
    main()