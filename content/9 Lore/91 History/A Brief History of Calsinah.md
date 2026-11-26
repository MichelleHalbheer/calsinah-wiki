---
publish: true
type: history
related_events: []
related_eras: []
tags:
  - history
date-created: 2026-11-16T14:54
date-updated: 2026-11-26T14:24
---

# A Brief History of Calsinah

A brief history of [[Calsinah]] as recorded by [[Ara'ash Om'rehn]] in their book [[On Times and Lifes Past]]

<!-- ORIGINAL BLOCK
```dataviewjs
const TIMELINE = "History of Calsinah";

function parseFcDate(fcDate) {
    if (!fcDate) return null;
    const m = String(fcDate).match(/^(-?\d+)-(\d+)-(\d+)$/);
    if (!m) return null;
   
    return {
        year: Number(m[1]),
        month: Number(m[2]),
        day: Number(m[3])
    };
}

function compareFcDates(a, b) {
    const da = parseFcDate(a);
    const db = parseFcDate(b);
   
    if (!da || !db) return 0;

    if (da.year !== db.year) return da.year - db.year;

    if (da.month !== db.month) return da.month - db.month;

    return da.day - db.day;
}

function inEra(eventDate, eraStart, eraEnd) {
    return (
        compareFcDates(eventDate, eraStart) >= 0 &&
        compareFcDates(eventDate, eraEnd) <= 0
    );

}

async function getEventBody(page) {
    const file = app.vault.getAbstractFileByPath(page.file.path);
    let text = await app.vault.cachedRead(file);

    // Remove frontmatter
	text = text.replace(/^---\n[\s\S]*?\n---\n*/, "");

	// Remove leading H1
	text = text.replace(/^# .*?\n+/m, "");
   
    const marker = "%%aat-event-end-of-body%%";
    const idx = text.indexOf(marker);

    if (idx >= 0)
        text = text.substring(0, idx);

    return text
		// [[Target#Heading|Display]] → Display
	    .replace(/\[\[[^|\]]+\|([^\]]+)\]\]/g, "$1")
	    // [[Target#Heading]] → Target
	    .replace(/\[\[([^#|\]]+)(?:#[^\]]*)?\]\]/g, "$1")
	    .replace(/\n+/g, " ")
	    .replace(/\|/g, "\\|")
	    .replace(/:/g, " -")
	    .trim();;
}

const eras = dv.pages()
		    .where(p =>
		        p.type == "historical_era" &&
		        p["aat-render-enabled"] === true &&
		        p["aat-timelines"] &&
		        p["aat-timelines"].includes(TIMELINE)
		    )
		    .array()
		    .sort((a, b) =>
			    compareFcDates(a["fc-date"], b["fc-date"])
		    );

const events = dv.pages()
			    .where(p =>
			        p.type == "historical_event" &&
			        p["aat-render-enabled"] === true &&
			        p["aat-timelines"] &&
			        p["aat-timelines"].includes(TIMELINE)
			    );

let mermaid = "timeline TD\n";

for (const era of eras) {
	const eraStart = parseFcDate(era["fc-date"]);
	const eraEnd = parseFcDate(era["fc-end"]);

	let eraStartString;
	let eraEndString;

	if (eraStart != null) {
		const eraStartYear = eraStart.year;
		if (eraStartYear >= 0) {
			eraStartString = `${eraStartYear} AFL`;
		} else {
			eraStartString = `${Math.abs(eraStartYear)} BFL`;
		}
	} else {
		eraStartString = "The Beginning of Time";
	}

	if (eraEnd != null) {
		const eraEndYear = eraEnd.year;
		if (eraEndYear >= 0) {
			eraEndString = `${eraEndYear} AFL`;
		} else {
			eraEndString = `${Math.abs(eraEndYear)} BFL`;
		}
	} else {
		eraEndString = "Today"
	}

    const eraTitle =
        `${era.file.name} • (${eraStartString} → ${eraEndString})`;
    mermaid += `    section ${eraTitle}\n`;

    const eraEvents = events
        .where(e => inEra(
            e["fc-date"],
            era["fc-date"],
            era["fc-end"]
        ))
        .array()
        .sort((a, b) =>
        compareFcDates(a["fc-date"], b["fc-date"]));

    for (const event of eraEvents) {
        const body = await getEventBody(event);
       
        const eventStart = parseFcDate(event["fc-date"]);
		const eventEnd = parseFcDate(event["fc-end"]);

		let eventStartString;
		let eventEndString;

		if (eventStart != null) {
			const eventStartYear = eventStart.year;
			if (eventStartYear >= 0) {
				eventStartString = `${eventStartYear} AFL`;
			} else {
				eventStartString = `${Math.abs(eventStartYear)} BFL`;
			}
		} else {
			eventStartString = "The Beginning of Time";
		}

		if (eventEnd != null) {
			const eventEndYear = eventEnd.year;
			if (eventEndYear >= 0) {
				eventEndString = `${eventEndYear} AFL`;
			} else {
				eventEndString = `${Math.abs(eventEndYear)} BFL`;
			}
		} else {
			eventEndString = "Today"
		}
        const dateLabel =
            event["fc-end"] &&
            event["fc-end"] !== event["fc-date"]
                ? `${eventStartString} → ${eventEndString}`
                : `${eventStartString}`;

        const title =
            `${event.file.name} • (${dateLabel})`;
        mermaid += `        ${title} : ${body}\n`;
    }
    mermaid += "\n";
}

dv.paragraph(
`~~~mermaid

${mermaid}

~~~`
);

function extractNoteName(label) {
    return label.split("•")[0].trim();
}

// Era headers
document.querySelectorAll("g.pele-section").forEach(section => {
    const note = extractNoteName(section.dataset.id ?? "");
    if (!note) return;
    section.style.cursor = "pointer";
    section.addEventListener("click", () => {
        app.workspace.openLinkText(note, "", false);
    });
});

// Event boxes AND event text
document.querySelectorAll("g.pele-period").forEach(period => {
    const note = extractNoteName(period.dataset.id ?? "");
    if (!note) return;
    period.style.cursor = "pointer";
    period.addEventListener("click", e => {
        e.stopPropagation();
        app.workspace.openLinkText(note, "", false);
    });
});
```
-->
<div class="block-language-dataviewjs node-insert-event" style="overflow-x: auto;"><p><span><div class="mermaid node-insert-event"><svg aria-roledescription="timeline" class="pele pele-timeline" fill="var(--_fg)" height="4366" role="graphics-document document" style='max-width:100%;height:auto;--_bg:var(--pele-bg,#fff);--_fg:var(--pele-fg,#1f1f1f);--_m:var(--pele-muted,#6e6e6e);--_l:var(--pele-line,#1f1f1f);--_s:var(--pele-surface,#f3f3f3);--_a:var(--pele-surface-alt,#e6e6e6);--_b:var(--pele-border,#8a8a8a);--_c:var(--pele-accent,#5b7bd5);color:var(--_fg);--_r:var(--pele-radius,4px);--_hw:var(--pele-heading-weight,bold);--_fm:var(--pele-font-mono,"??", "??", ui-monospace, SFMono-Regular, "Cascadia Mono", "Roboto Mono", "DejaVu Sans Mono", "Liberation Mono", Menlo, Monaco, "Consolas", "Source Code Pro", monospace);font:16px sans-serif;letter-spacing:normal;word-spacing:normal;text-transform:none;direction:ltr;font-family:var(--pele-font,"??", "??", ui-sans-serif, -apple-system, BlinkMacSystemFont, system-ui, "Segoe UI", "Google Sans Flex", Roboto, "Inter Variable", "Inter", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif)' viewbox="0 0 528 4366" width="528" xmlns="http://www.w3.org/2000/svg"><path class="pele-axis" d="M204,8V4351" fill="none" stroke="var(--_l)"></path><path class="pele-marker" d="M204,4358L200.64,4350L207.36,4350Z" fill="var(--_l)" stroke="none"></path><g class="pele-cluster pele-section" data-id="The Compounding • (200000 BFL → 90001 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-1,#4c78a8)" height="40" style="rx:var(--_r)" width="512" x="8" y="8"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="33.6">The Compounding • (200000 BFL → 90001 BFL)</tspan></text></g><g class="pele-cluster pele-section" data-id="The Draconic Ages • (90000 BFL → 54001 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-2,#f58518)" height="40" style="rx:var(--_r)" width="512" x="8" y="68"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="93.6">The Draconic Ages • (90000 BFL → 54001 BFL)</tspan></text><g class="pele-node pele-period" data-id="Birth of Bahamut and Tiamat • (90000 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-2,#f58518)" height="58" style="rx:var(--_r)" width="176" x="8" y="198"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="222.1">Birth of Bahamut and</tspan><tspan x="96" y="243.1">Tiamat • (90000 BFL)</tspan></text><path class="pele-edge" d="M184,227H204M218,227H232M204,227H218V227" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="227" fill="var(--pele-series-2,#f58518)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-2,#f58518)" fill-opacity="0.16" height="214" style="rx:var(--_r)" width="288" x="232" y="120"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="141.9">From the essence of the elements twin</tspan><tspan x="376" y="159.9">deities were born. And though both</tspan><tspan x="376" y="177.9">stemmed from the same essence, they</tspan><tspan x="376" y="195.9">were like two sides of a coin. One was</tspan><tspan x="376" y="213.9">known as Bahamut, the Platinum Dragon,</tspan><tspan x="376" y="231.9">the god of justice and nobility. The other</tspan><tspan x="376" y="249.9">became known as Tiamat, the Queen of</tspan><tspan x="376" y="267.9">Chaos, goddess of wealth, greed and</tspan><tspan x="376" y="285.9">vengeance. The twin gods would forever</tspan><tspan x="376" y="303.9">oppose each other and so would their</tspan><tspan x="376" y="321.9">spawn.</tspan></text></g></g><g class="pele-node pele-period" data-id="Birth of Dragonkind • (80000 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-2,#f58518)" height="58" style="rx:var(--_r)" width="176" x="8" y="432"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="456.1">Birth of Dragonkind •</tspan><tspan x="96" y="477.1">(80000 BFL)</tspan></text><path class="pele-edge" d="M184,461H204M218,461H232M204,461H218V461" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="461" fill="var(--pele-series-2,#f58518)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-2,#f58518)" fill-opacity="0.16" height="214" style="rx:var(--_r)" width="288" x="232" y="354"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="375.9">From the first deities of Calsinah spawned</tspan><tspan x="376" y="393.9">the first sentient life. In their own image</tspan><tspan x="376" y="411.9">they created dragonkind. Tiamat formed</tspan><tspan x="376" y="429.9">the Chromatic Dragons, who follow her</tspan><tspan x="376" y="447.9">goals, while Bahamut created the Metallic</tspan><tspan x="376" y="465.9">Dragons in his likeness. Despite always</tspan><tspan x="376" y="483.9">opposing each other and persisting</tspan><tspan x="376" y="501.9">conflict, for many millennia, dragonkind</tspan><tspan x="376" y="519.9">would life in relativ peace and share</tspan><tspan x="376" y="537.9">Calsinah with each other and their</tspan><tspan x="376" y="555.9">forefathers of the elements.</tspan></text></g></g></g><g class="pele-cluster pele-section" data-id="The Age of Divinity • (54000 BFL → 23001 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-3,#54a24b)" height="40" style="rx:var(--_r)" width="512" x="8" y="588"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="613.6">The Age of Divinity • (54000 BFL → 23001 BFL)</tspan></text></g><g class="pele-cluster pele-section" data-id="The First Sundering • (23000 BFL → 10001 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-4,#e45756)" height="40" style="rx:var(--_r)" width="512" x="8" y="648"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="673.6">The First Sundering • (23000 BFL → 10001 BFL)</tspan></text></g><g class="pele-cluster pele-section" data-id="The High Age • (10000 BFL → 5001 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-5,#72b7b2)" height="40" style="rx:var(--_r)" width="512" x="8" y="708"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="733.6">The High Age • (10000 BFL → 5001 BFL)</tspan></text><g class="pele-node pele-period" data-id="The Investiture • (10000 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-5,#72b7b2)" height="58" style="rx:var(--_r)" width="176" x="8" y="838"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="862.1">The Investiture •</tspan><tspan x="96" y="883.1">(10000 BFL)</tspan></text><path class="pele-edge" d="M184,867H204M218,867H232M204,867H218V867" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="867" fill="var(--pele-series-5,#72b7b2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-5,#72b7b2)" fill-opacity="0.16" height="214" style="rx:var(--_r)" width="288" x="232" y="760"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="781.9">When at the end of The First Sundering</tspan><tspan x="376" y="799.9">the veil between planes briefly collapsed,</tspan><tspan x="376" y="817.9">the land got suffused by otherworldly</tspan><tspan x="376" y="835.9">energy, leaving behind powerful ley lines</tspan><tspan x="376" y="853.9">and magically affine creatures such as the</tspan><tspan x="376" y="871.9">Elves, Dwarves and Gnomes got invested</tspan><tspan x="376" y="889.9">by the energy of other realms. In most</tspan><tspan x="376" y="907.9">places the veil was restored by the</tspan><tspan x="376" y="925.9">winning gods quickly, but in some places</tspan><tspan x="376" y="943.9">the veil remains broken or thinned, leaving</tspan><tspan x="376" y="961.9">behind gateway to other planes.</tspan></text></g></g></g><g class="pele-cluster pele-section" data-id="The Second Sundering • (5000 BFL → 2301 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-6,#eeca3b)" height="40" style="rx:var(--_r)" width="512" x="8" y="994"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="1019.6">The Second Sundering • (5000 BFL → 2301 BFL)</tspan></text></g><g class="pele-cluster pele-section" data-id="The Age of Transformation • (2300 BFL → 0 AFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="40" style="rx:var(--_r)" width="512" x="8" y="1054"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="1079.6">The Age of Transformation • (2300 BFL → 0 AFL)</tspan></text><g class="pele-node pele-period" data-id="Arcane Revolution of Aashin • (764 BFL → 759 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="79" style="rx:var(--_r)" width="176" x="8" y="1155.5"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="1179.6">Arcane Revolution of</tspan><tspan x="96" y="1200.6">Aashin • (764 BFL →</tspan><tspan x="96" y="1221.6">759 BFL)</tspan></text><path class="pele-edge" d="M184,1195H204M218,1195H232M204,1195H218V1195" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="1195" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="178" style="rx:var(--_r)" width="288" x="232" y="1106"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="1127.9">The Arcane Revolution of Aashin followed</tspan><tspan x="376" y="1145.9">the year long mistreatment of mages in</tspan><tspan x="376" y="1163.9">the Aashin Sovereignty. In the process the</tspan><tspan x="376" y="1181.9">Aashin royal family was executed and the</tspan><tspan x="376" y="1199.9">Triumvirate of Lysoov was established as</tspan><tspan x="376" y="1217.9">the new governing body. The Aashin</tspan><tspan x="376" y="1235.9">Sovereignty was renamed to the Dominion</tspan><tspan x="376" y="1253.9">of Riaaroshin and was ruled as a</tspan><tspan x="376" y="1271.9">magocracy following the revolution.</tspan></text></g></g><g class="pele-node pele-period" data-id="Birth of Iahl • (709 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="1328"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="1352.1">Birth of Iahl • (709</tspan><tspan x="96" y="1373.1">BFL)</tspan></text><path class="pele-edge" d="M184,1357H204M218,1357H232M204,1357H218V1357" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="1357" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="106" style="rx:var(--_r)" width="288" x="232" y="1304"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="1325.9">Iahl was a sorcerer born to tremendous</tspan><tspan x="376" y="1343.9">power and talent. He would hone his</tspan><tspan x="376" y="1361.9">powers relentlessly, eventuall ascending to</tspan><tspan x="376" y="1379.9">godhood and becoming the god king of</tspan><tspan x="376" y="1397.9">the Vibrosyhn Empire.</tspan></text></g></g><g class="pele-node pele-period" data-id="Founding of the College of Ascendancy • (621 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="100" style="rx:var(--_r)" width="176" x="8" y="1505"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="1529.1">Founding of the</tspan><tspan x="96" y="1550.1">College of</tspan><tspan x="96" y="1571.1">Ascendancy • (621</tspan><tspan x="96" y="1592.1">BFL)</tspan></text><path class="pele-edge" d="M184,1555H204M218,1555H232M204,1555H218V1555" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="1555" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="250" style="rx:var(--_r)" width="288" x="232" y="1430"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="1451.9">Among the Triumvirate of Lysoov's primary</tspan><tspan x="376" y="1469.9">goals was the study and improvement of</tspan><tspan x="376" y="1487.9">the arcane arts. As such, the second</tspan><tspan x="376" y="1505.9">generation of the Triumvirate established</tspan><tspan x="376" y="1523.9">the College of Ascendancy in Jiimar. It was</tspan><tspan x="376" y="1541.9">established with twelve faculties,</tspan><tspan x="376" y="1559.9">specializing in different aspects of the</tspan><tspan x="376" y="1577.9">arcane, though they were distinct from the</tspan><tspan x="376" y="1595.9">schools of magic as they are known today.</tspan><tspan x="376" y="1613.9">The college was the most prestigious</tspan><tspan x="376" y="1631.9">institution in the Dominion of Riaaroshin</tspan><tspan x="376" y="1649.9">and developed tremendous political</tspan><tspan x="376" y="1667.9">influence over the time if it's existence.</tspan></text></g></g><g class="pele-node pele-period" data-id="The Extinguishment • (602 BFL → 594 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="1823"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="1847.1">The Extinguishment •</tspan><tspan x="96" y="1868.1">(602 BFL → 594 BFL)</tspan></text><path class="pele-edge" d="M184,1852H204M218,1852H232M204,1852H218V1852" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="1852" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="304" style="rx:var(--_r)" width="288" x="232" y="1700"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="1721.9">The Vibrosyhn Martial Court outlawed the</tspan><tspan x="376" y="1739.9">use of magic for any use other than</tspan><tspan x="376" y="1757.9">purposes of state, calling for all mages to</tspan><tspan x="376" y="1775.9">register with the government. Any mage</tspan><tspan x="376" y="1793.9">presumed to be using the arcane arts</tspan><tspan x="376" y="1811.9">outside of approved uses was arrested</tspan><tspan x="376" y="1829.9">and executed without trial. In 597 BFL the</tspan><tspan x="376" y="1847.9">use of magic was banned completely and</tspan><tspan x="376" y="1865.9">all mages were to be executed. Already,</tspan><tspan x="376" y="1883.9">many of the more resourceful casters had</tspan><tspan x="376" y="1901.9">gone into hiding, with more following</tspan><tspan x="376" y="1919.9">after the ban. This policy would eventually</tspan><tspan x="376" y="1937.9">lead to an uprising led by a group of</tspan><tspan x="376" y="1955.9">exiled archmages, who had called upon</tspan><tspan x="376" y="1973.9">Iahl to aid them, resulting in Iahl taking</tspan><tspan x="376" y="1991.9">the Vibrosyhn throne as god king.</tspan></text></g></g><g class="pele-node pele-period" data-id="Ascension of Iahl • (598 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="2066"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="2090.1">Ascension of Iahl •</tspan><tspan x="96" y="2111.1">(598 BFL)</tspan></text><path class="pele-edge" d="M184,2095H204M218,2095H232M204,2095H218V2095" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="2095" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="142" style="rx:var(--_r)" width="288" x="232" y="2024"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="2045.9">The powerful sorcerer Iahl was known to</tspan><tspan x="376" y="2063.9">aid any in need using his powers.</tspan><tspan x="376" y="2081.9">Additionally, he was well known for</tspan><tspan x="376" y="2099.9">developing unique spells or amenities of</tspan><tspan x="376" y="2117.9">the arcane. In 598 BFL he ascended to</tspan><tspan x="376" y="2135.9">godhood, making him the god of progress</tspan><tspan x="376" y="2153.9">and benevolence.</tspan></text></g></g><g class="pele-node pele-period" data-id="The Spring of Mages • (594 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="2291"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="2315.1">The Spring of Mages</tspan><tspan x="96" y="2336.1">• (594 BFL)</tspan></text><path class="pele-edge" d="M184,2320H204M218,2320H232M204,2320H218V2320" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="2320" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="268" style="rx:var(--_r)" width="288" x="232" y="2186"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="2207.9">Following the total ban of magic by the</tspan><tspan x="376" y="2225.9">Vibrosyhn Martial Court and the brutal</tspan><tspan x="376" y="2243.9">persecution of mages in the Vibrosyhn</tspan><tspan x="376" y="2261.9">Empire, numerous mages fled and went</tspan><tspan x="376" y="2279.9">into hiding. Iahl, who had newly ascended</tspan><tspan x="376" y="2297.9">to godhood, was called upon by his</tspan><tspan x="376" y="2315.9">followers to aid them. Seeing the pain</tspan><tspan x="376" y="2333.9">caused by the Vibrosyhn Martial Court and</tspan><tspan x="376" y="2351.9">the stop it put to progress, Iahl killed the</tspan><tspan x="376" y="2369.9">members of the Martial Court and with a</tspan><tspan x="376" y="2387.9">group of Archmages in hiding established</tspan><tspan x="376" y="2405.9">himself as god king of the Vibrosyhn</tspan><tspan x="376" y="2423.9">Empire, ushering in an age of progress</tspan><tspan x="376" y="2441.9">and wealth.</tspan></text></g></g><g class="pele-node pele-period" data-id="Uprising of Jiimar • (431 BFL → 429 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="2642"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="2666.1">Uprising of Jiimar •</tspan><tspan x="96" y="2687.1">(431 BFL → 429 BFL)</tspan></text><path class="pele-edge" d="M184,2671H204M218,2671H232M204,2671H218V2671" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="2671" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="394" style="rx:var(--_r)" width="288" x="232" y="2474"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="2495.9">With the College of Ascendancy growing</tspan><tspan x="376" y="2513.9">more and more powerful, the Triumvirate</tspan><tspan x="376" y="2531.9">of Lysoov started imposing more and</tspan><tspan x="376" y="2549.9">more restrictions on the magic activities of</tspan><tspan x="376" y="2567.9">the public and the development of power</tspan><tspan x="376" y="2585.9">and the arcane arts at the college. In 431</tspan><tspan x="376" y="2603.9">BFL the arrest of several students of the</tspan><tspan x="376" y="2621.9">College lead to student protests, which</tspan><tspan x="376" y="2639.9">quickly escalated. Many faculty members,</tspan><tspan x="376" y="2657.9">in particular the twelve heads of faculty -</tspan><tspan x="376" y="2675.9">known as the twelve Ancients - supported</tspan><tspan x="376" y="2693.9">the students in their protests, which</tspan><tspan x="376" y="2711.9">resulted in the Triumvirate of Lysoov being</tspan><tspan x="376" y="2729.9">removed from power by the Ancients in</tspan><tspan x="376" y="2747.9">429 BFL. The result was the establishment</tspan><tspan x="376" y="2765.9">of the Congregate of Ancients as the new</tspan><tspan x="376" y="2783.9">power of state. While the Triumvirate</tspan><tspan x="376" y="2801.9">already aimed to improve the powers they</tspan><tspan x="376" y="2819.9">wielded, the Congregate of Ancients had</tspan><tspan x="376" y="2837.9">an agenda that pursued this goal far more</tspan><tspan x="376" y="2855.9">ruthlessly.</tspan></text></g></g><g class="pele-node pele-period" data-id="Seizing of the Primordial Forge and Battle of Uaynahr • (339 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="100" style="rx:var(--_r)" width="176" x="8" y="2936"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="2960.1">Seizing of the</tspan><tspan x="96" y="2981.1">Primordial Forge and</tspan><tspan x="96" y="3002.1">Battle of Uaynahr •</tspan><tspan x="96" y="3023.1">(339 BFL)</tspan></text><path class="pele-edge" d="M184,2986H204M218,2986H232M204,2986H218V2986" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="2986" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="196" style="rx:var(--_r)" width="288" x="232" y="2888"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="2909.9">As the Congregate of Ancients started</tspan><tspan x="376" y="2927.9">pursuing their goal of ultimate arcane</tspan><tspan x="376" y="2945.9">power more and more ruthlessly, they</tspan><tspan x="376" y="2963.9">started eyeing the achievements of the</tspan><tspan x="376" y="2981.9">Vibrosyhn Empire under Iahl rule more</tspan><tspan x="376" y="2999.9">and more jealously. So, eventually, the</tspan><tspan x="376" y="3017.9">seized the Primordial Forge, one of the</tspan><tspan x="376" y="3035.9">core achievements of research under Iahl.</tspan><tspan x="376" y="3053.9">This lead to the Battle of Uaynahr and</tspan><tspan x="376" y="3071.9">triggered the War of the Arcane.</tspan></text></g></g><g class="pele-node pele-period" data-id="War of the Arcane • (339 BFL → 0 AFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="3119"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="3143.1">War of the Arcane •</tspan><tspan x="96" y="3164.1">(339 BFL → 0 AFL)</tspan></text><path class="pele-edge" d="M184,3148H204M218,3148H232M204,3148H218V3148" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="3148" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="88" style="rx:var(--_r)" width="288" x="232" y="3104"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="3125.9">The War of the Arcane was a major,</tspan><tspan x="376" y="3143.9">centuries long war between the Vibrosyhn</tspan><tspan x="376" y="3161.9">Empire and the Dominion of Riaaroshin,</tspan><tspan x="376" y="3179.9">culminating in the Fall of Limihn.</tspan></text></g></g><g class="pele-node pele-period" data-id="Siege of Quadiin • (38 BFL → 6 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="3290"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="3314.1">Siege of Quadiin •</tspan><tspan x="96" y="3335.1">(38 BFL → 6 BFL)</tspan></text><path class="pele-edge" d="M184,3319H204M218,3319H232M204,3319H218V3319" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="3319" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="214" style="rx:var(--_r)" width="288" x="232" y="3212"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="3233.9">The Siege of Quadiin was on of the major</tspan><tspan x="376" y="3251.9">engagements in the War of the Arcane.</tspan><tspan x="376" y="3269.9">Following a steady advance by the</tspan><tspan x="376" y="3287.9">Vibrosyhn Empire on Riaaroshin positions,</tspan><tspan x="376" y="3305.9">they eventually reached Quadiin, one of</tspan><tspan x="376" y="3323.9">the most important cities in the Dominion</tspan><tspan x="376" y="3341.9">of Riaaroshin. After a prolonged siege,</tspan><tspan x="376" y="3359.9">Riaaroshin forces eventually managed to</tspan><tspan x="376" y="3377.9">break the siege and free the city but at</tspan><tspan x="376" y="3395.9">great cost, leaving them severely</tspan><tspan x="376" y="3413.9">weakened.</tspan></text></g></g><g class="pele-node pele-period" data-id="Retaking of the Primordial Forge • (3 BFL → 3 BFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="79" style="rx:var(--_r)" width="176" x="8" y="3513.5"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="3537.6">Retaking of the</tspan><tspan x="96" y="3558.6">Primordial Forge • (3</tspan><tspan x="96" y="3579.6">BFL → 3 BFL)</tspan></text><path class="pele-edge" d="M184,3553H204M218,3553H232M204,3553H218V3553" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="3553" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="214" style="rx:var(--_r)" width="288" x="232" y="3446"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="3467.9">After the Siege of Quadiin, the Riaaroshin</tspan><tspan x="376" y="3485.9">forces were left severly weakened by the</tspan><tspan x="376" y="3503.9">battle and a large movement of troops</tspan><tspan x="376" y="3521.9">was necessary to eventually break the</tspan><tspan x="376" y="3539.9">siege. This allowed for the Vibrosyhn</tspan><tspan x="376" y="3557.9">Empire to finally retake the Primordial</tspan><tspan x="376" y="3575.9">Forge, taking away the one edge the</tspan><tspan x="376" y="3593.9">Riaaroshin had left in the war. This loss</tspan><tspan x="376" y="3611.9">eventually led the Congregate of Ancients</tspan><tspan x="376" y="3629.9">to casting The Moonstrike in hopes of</tspan><tspan x="376" y="3647.9">retaking the war.</tspan></text></g></g><g class="pele-node pele-period" data-id="The Moonstrike • (0 AFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="3812"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="3836.1">The Moonstrike • (0</tspan><tspan x="96" y="3857.1">AFL)</tspan></text><path class="pele-edge" d="M184,3841H204M218,3841H232M204,3841H218V3841" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="3841" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="322" style="rx:var(--_r)" width="288" x="232" y="3680"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="3701.9">The Moonstrike marked the culmination of</tspan><tspan x="376" y="3719.9">the War of the Arcane. After decades of</tspan><tspan x="376" y="3737.9">bloody war, the Congregate of Ancients</tspan><tspan x="376" y="3755.9">decided to end the war by destroying their</tspan><tspan x="376" y="3773.9">enemies of the Vibrosyhn Empire through</tspan><tspan x="376" y="3791.9">a ritual casting, calling upon the power of</tspan><tspan x="376" y="3809.9">the moon and levelling the city of</tspan><tspan x="376" y="3827.9">Hariosylth. For this, all twelve of them</tspan><tspan x="376" y="3845.9">gathered on Mount Aossiin to perform a</tspan><tspan x="376" y="3863.9">ritual on a scale that has never before</tspan><tspan x="376" y="3881.9">been seen on Calsinah. While the casting</tspan><tspan x="376" y="3899.9">was successful and Hariosylth was</tspan><tspan x="376" y="3917.9">destroyed completely, leaving nothing but</tspan><tspan x="376" y="3935.9">a vitrified track, known as the Scar of</tspan><tspan x="376" y="3953.9">Hariosylth, behind, it drained Limihn of its</tspan><tspan x="376" y="3971.9">essence almost completely, causing its</tspan><tspan x="376" y="3989.9">subsequent fall.</tspan></text></g></g><g class="pele-node pele-period" data-id="Fall of Limihn • (0 AFL)" style="cursor: pointer;"><rect fill="var(--pele-series-7,#b279a2)" height="58" style="rx:var(--_r)" width="176" x="8" y="4091"></rect><text fill="var(--_bg)" text-anchor="middle" xml:space="preserve"><tspan x="96" y="4115.1">Fall of Limihn • (0</tspan><tspan x="96" y="4136.1">AFL)</tspan></text><path class="pele-edge" d="M184,4120H204M218,4120H232M204,4120H218V4120" fill="none" stroke="var(--_b)"></path><circle class="pele-dot" cx="204" cy="4120" fill="var(--pele-series-7,#b279a2)" r="4" stroke="var(--_bg)" stroke-width="2"></circle><g class="pele-node pele-event"><rect fill="var(--pele-series-7,#b279a2)" fill-opacity="0.16" height="196" style="rx:var(--_r)" width="288" x="232" y="4022"></rect><text font-size="14" text-anchor="middle" xml:space="preserve"><tspan x="376" y="4043.9">Following the ritual casting of The</tspan><tspan x="376" y="4061.9">Moonstrike by the Congregate of Ancients</tspan><tspan x="376" y="4079.9">and the ensuing destruction Hariosylth,</tspan><tspan x="376" y="4097.9">Limihn, the first moon of Clasinah, lost its</tspan><tspan x="376" y="4115.9">essence and began to fall. The Fall of</tspan><tspan x="376" y="4133.9">Limihn therefore marks the most</tspan><tspan x="376" y="4151.9">cataclysmic event in the modern history of</tspan><tspan x="376" y="4169.9">Calsinah, wiping out most major kingdoms</tspan><tspan x="376" y="4187.9">from before the fall and forcing civilization</tspan><tspan x="376" y="4205.9">mostly underground for years to follow.</tspan></text></g></g></g><g class="pele-cluster pele-section" data-id="The Age of Darkness • (0 AFL → 212 AFL)" style="cursor: pointer;"><rect fill="var(--pele-series-8,#9d755d)" height="40" style="rx:var(--_r)" width="512" x="8" y="4238"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="4263.6">The Age of Darkness • (0 AFL → 212 AFL)</tspan></text></g><g class="pele-cluster pele-section" data-id="The Resurgency • (213 AFL → Today)" style="cursor: pointer;"><rect fill="var(--pele-series-1,#4c78a8)" height="40" style="rx:var(--_r)" width="512" x="8" y="4298"></rect><text fill="var(--_bg)" font-weight="var(--_hw)" text-anchor="middle" xml:space="preserve"><tspan x="264" y="4323.6">The Resurgency • (213 AFL → Today)</tspan></text></g></svg></div></span></p></div>

## Origins

## Development

## Major Turning Points

## Legacy

## Related Events

## Notes
